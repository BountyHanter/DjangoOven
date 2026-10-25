import logging
import os
import select
import shutil
import subprocess
import tempfile
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from main_app.management.commands.utils.parser.config import HEADERS
from main_app.management.commands.utils.parser.extractors import get_extractor
from main_app.management.commands.utils.parser.schemas import FetchResult


logger = logging.getLogger(__name__)
BODY_PREVIEW_LIMIT = 1200
DIAGNOSTIC_HEADERS = (
    "location", "content-type", "server", "refresh", "retry-after",
    "via", "x-cache", "cf-ray", "cf-mitigated",
)


@contextmanager
def _browser_environment(virtual_display: bool) -> Iterator[dict[str, str] | None]:
    if not virtual_display:
        yield None
        return

    executable = shutil.which("Xvfb")
    if not executable:
        raise RuntimeError(
            "Не найден Xvfb. Установи пакет xvfb для запуска с виртуальным экраном."
        )

    # Xvfb сам выбирает свободный DISPLAY и сообщает о готовности через pipe.
    read_fd, write_fd = os.pipe()
    process = None
    try:
        with tempfile.TemporaryFile(mode="w+t") as error_log:
            try:
                try:
                    process = subprocess.Popen(
                        [
                            executable, "-displayfd", str(write_fd),
                            "-screen", "0", "1365x900x24", "-nolisten", "tcp",
                        ],
                        pass_fds=(write_fd,),
                        stdout=subprocess.DEVNULL,
                        stderr=error_log,
                    )
                finally:
                    os.close(write_fd)

                ready, _, _ = select.select([read_fd], [], [], 10)
                display_number = os.read(read_fd, 32).decode().strip() if ready else ""
                if not display_number.isdecimal() or process.poll() is not None:
                    error_log.seek(0)
                    raise RuntimeError(f"Xvfb не запустился: {error_log.read(1200)}")

                environment = os.environ.copy()
                environment["DISPLAY"] = f":{display_number}"
                # Chrome должен выбрать виртуальный X11, даже на рабочем столе Wayland.
                environment.pop("WAYLAND_DISPLAY", None)
                environment.pop("XAUTHORITY", None)
                logger.debug("Виртуальный экран готов: DISPLAY=%s", environment["DISPLAY"])
                yield environment
            finally:
                if process is not None:
                    if process.poll() is None:
                        process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
    finally:
        os.close(read_fd)


def _log_response(
    url: str,
    status_code: int,
    reason: str,
    headers: Mapping[str, str],
) -> None:
    logger.debug("Ответ: %s %s | URL: %s", status_code, reason, url)
    for name in DIAGNOSTIC_HEADERS:
        if name in headers:
            logger.debug("  %s: %s", name, headers[name])

    if 300 <= status_code < 400:
        location = headers.get("location")
        if location:
            logger.debug("Редирект: %s -> %s", url, urljoin(url, location))
        else:
            logger.debug("Ответ %s без заголовка Location", status_code)


def _log_http_response(response: httpx.Response) -> None:
    _log_response(
        str(response.url), response.status_code,
        response.reason_phrase, response.headers,
    )


def _log_body_preview(html: str, status_code: int | None) -> None:
    if status_code != 200:
        logger.debug(
            "Тело ответа (%s символов, показано не более %s): %r",
            len(html), BODY_PREVIEW_LIMIT, html[:BODY_PREVIEW_LIMIT],
        )


def build_result(
    url: str,
    status_code: int | None,
    html: str | None,
    error_text: str | None = None,
) -> FetchResult:
    """
    Универсальный билдер результата:
    - выбирает extractor по домену
    - обрабатывает 200 / 404 / ошибки
    """

    answer = FetchResult()

    # ---- нормальная страница ----
    if status_code == 200 and html:
        # получаем extractor под конкретный домен
        extractor = get_extractor(url)

        if extractor:
            try:
                result = extractor(html)
            except Exception as e:
                # если парсер упал — фиксируем как ошибку
                logger.error("Ошибка extractor для URL %s: %s", url, e)
                logger.debug("Подробности ошибки extractor", exc_info=True)
                answer.status_code = status_code
                answer.error_text = f"extract_error: {e}"
                return answer
        else:
            # если extractor не найден — это твоя ошибка конфигурации
            logger.error("Не найден extractor для URL: %s", url)
            answer.status_code = status_code
            answer.error_text = "no_extractor_for_domain"
            return answer

        answer.status_code = status_code
        answer.data = result
        return answer

    # ---- товар удалён (чистый 404) ----
    if status_code in (404,):
        answer.status_code = status_code
        return answer

    # ---- страница есть, но внутри текст 404 ----
    if html and "Страница не найдена" in html:
        return FetchResult(status_code=404)

    # ---- прочие ошибки (таймауты, 500 и тд) ----
    answer.status_code = status_code
    answer.error_text = error_text
    return answer


def fetch_html(url: str, *, follow_redirects: bool = False) -> FetchResult:
    logger.info("HTTP GET: %s", url)
    try:
        # обычный HTTP-запрос (быстро и дёшево)
        with httpx.Client(
            timeout=30,
            headers=HEADERS,
            follow_redirects=follow_redirects,
            event_hooks={"response": [_log_http_response]},
        ) as client:
            response = client.get(url)

        _log_body_preview(response.text, response.status_code)
        return build_result(
            url=url,
            status_code=response.status_code,
            html=response.text,
            error_text=response.reason_phrase,
        )

    except Exception as e:
        # любая ошибка сети / таймаут / DNS
        logger.error("Ошибка HTTP-запроса для URL %s: %s", url, e)
        logger.debug("Подробности ошибки HTTP-запроса", exc_info=True)
        return build_result(
            url=url,
            status_code=None,
            html=None,
            error_text=str(e),
        )


def fetch_html_playwright(
    url: str,
    *,
    headless: bool = True,
    wait_timeout_ms: int = 30_000,
    profile_dir: str | Path | None = None,
    channel: str | None = None,
    reduce_automation_signals: bool = False,
    virtual_display: bool = False,
) -> FetchResult:
    """Загружает страницу; для kamin.ru ожидает возврат с проверки к товару."""
    logger.info("Playwright GET: %s", url)
    try:
        if virtual_display and headless:
            raise ValueError("Для virtual_display=True нужен headless=False")
        # браузер для сложных сайтов (JS, защита и тд)
        with _browser_environment(virtual_display) as environment, sync_playwright() as p:
            browser = None
            context = None
            try:
                # User-Agent и HTTP-заголовки формирует сам браузер.
                context_options = {
                    "locale": "ru-RU",
                    "viewport": {"width": 1365, "height": 900},
                }
                launch_options = {"headless": headless}
                if environment is not None:
                    launch_options["env"] = environment
                    launch_options["args"] = ["--ozone-platform=x11"]
                if channel:
                    launch_options["channel"] = channel
                if reduce_automation_signals:
                    # Эксперимент: сравниваем поведение сайта без стандартного
                    # флага автоматизации Chrome. Это не гарантирует проход проверки.
                    launch_options["ignore_default_args"] = ["--enable-automation"]
                    launch_options.setdefault("args", []).append(
                        "--disable-blink-features=AutomationControlled"
                    )
                    logger.debug("Включён экспериментальный режим запуска Chrome")

                if profile_dir is not None:
                    profile_path = Path(profile_dir).expanduser().resolve()
                    logger.debug("Постоянный профиль браузера: %s", profile_path)
                    context = p.chromium.launch_persistent_context(
                        user_data_dir=str(profile_path),
                        **launch_options,
                        **context_options,
                    )
                else:
                    browser = p.chromium.launch(**launch_options)
                    context = browser.new_context(**context_options)

                page = context.pages[0] if context.pages else context.new_page()
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        "Браузер: %s | сохранённых cookies для сайта: %s",
                        channel or "chromium", len(context.cookies([url])),
                    )
                    logger.debug(
                        "Параметры браузера: %s",
                        page.evaluate("""() => ({
                            webdriver: navigator.webdriver,
                            userAgent: navigator.userAgent,
                            platform: navigator.platform,
                            languages: navigator.languages
                        })"""),
                    )
                page.on(
                    "pageerror",
                    lambda error: logger.debug("Ошибка JavaScript: %s", error),
                )

                def on_console(message):
                    if message.type in {"warning", "error"}:
                        logger.debug("Console %s: %s", message.type, message.text)

                def on_request_failed(request):
                    if request.resource_type in {"document", "script", "xhr", "fetch"}:
                        logger.debug(
                            "Не загружен ресурс [%s]: %s | %s",
                            request.resource_type, request.url, request.failure,
                        )

                page.on("console", on_console)
                page.on("requestfailed", on_request_failed)
                latest_response = None

                def on_response(response):
                    nonlocal latest_response
                    if (
                        response.status >= 400
                        and response.request.resource_type in {"script", "xhr", "fetch"}
                    ):
                        logger.debug(
                            "Ошибка ресурса: HTTP %s | %s", response.status, response.url,
                        )
                    # Учитываем документы основной страницы, включая переходы из JS.
                    if (
                        response.request.is_navigation_request()
                        and response.frame == page.main_frame
                    ):
                        latest_response = response
                        _log_response(
                            response.url, response.status,
                            response.status_text, response.headers,
                        )

                page.on("response", on_response)
                target = urlparse(url)
                is_kamin = target.hostname in {"kamin.ru", "www.kamin.ru"}
                page.goto(
                    url,
                    wait_until="domcontentloaded" if is_kamin else "load",
                    timeout=wait_timeout_ms,
                )
                on_check_page = urlparse(page.url).path == "/check_captcha.php"

                if is_kamin and (
                    on_check_page
                    or (latest_response is not None and latest_response.status == 200)
                ):
                    stage = "browser_check_timeout"
                    try:
                        logger.debug(
                            "Ожидание возврата к товару (до %s мс) | URL: %s",
                            wait_timeout_ms, page.url,
                        )
                        if on_check_page and not headless and not virtual_display:
                            logger.info(
                                "Браузер открыт: при необходимости пройди проверку вручную. "
                                "После возврата к товару извлечение продолжится автоматически."
                            )

                        def is_product_url(current_url):
                            current = urlparse(current_url)
                            return (
                                current.hostname in {"kamin.ru", "www.kamin.ru"}
                                and current.path.rstrip("/") == target.path.rstrip("/")
                                and current.path != "/check_captcha.php"
                            )

                        page.wait_for_url(
                            is_product_url,
                            wait_until="domcontentloaded",
                            timeout=wait_timeout_ms,
                        )
                        # Ожидаем блок, который использует extractor kamin.ru.
                        # Для удалённого товара с HTTP 404 этот блок не требуется.
                        if latest_response is not None and latest_response.status == 200:
                            stage = "product_content_timeout"
                            page.locator("aside").first.wait_for(
                                state="attached", timeout=wait_timeout_ms,
                            )
                        if not is_product_url(page.url):
                            return FetchResult(
                                error_text=f"browser_check_not_completed: {page.url}",
                            )
                    except PlaywrightTimeoutError:
                        if (
                            is_product_url(page.url)
                            and latest_response is not None
                            and latest_response.status != 200
                        ):
                            return build_result(
                                url=url,
                                status_code=latest_response.status,
                                html=page.content(),
                                error_text=latest_response.status_text,
                            )
                        if urlparse(page.url).path == "/check_captcha.php":
                            stage = "browser_check_timeout"
                        error_text = f"{stage}: URL={page.url}; timeout={wait_timeout_ms}ms"
                        logger.warning("%s", error_text)
                        # Не передаём страницу проверки в extractor: отсутствие
                        # aside на ней не означает, что товара нет в наличии.
                        return FetchResult(error_text=error_text)

                status_code = latest_response.status if latest_response else None
                html = page.content()
                logger.debug("URL страницы после загрузки: %s", page.url)
                _log_body_preview(html, status_code)
            finally:
                # Закрытие постоянного контекста сохраняет профиль для следующего запуска.
                if context is not None:
                    context.close()
                if browser is not None:
                    browser.close()

        return build_result(
            url=url,
            status_code=status_code,
            html=html,
            error_text=latest_response.status_text if latest_response else "no_navigation_response",
        )

    except Exception as e:
        logger.error("Ошибка Playwright для URL %s: %s", url, e)
        logger.debug("Подробности ошибки Playwright", exc_info=True)
        return build_result(
            url=url,
            status_code=None,
            html=None,
            error_text=str(e),
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    # Отдельный тестовый профиль; повторные запуски используют его cookies.
    test_browser_options = {
        "headless": False,
        "virtual_display": True,
        "channel": "chrome",
        "reduce_automation_signals": True,
        "wait_timeout_ms": 120_000,
        # Новый профиль нужен для проверки без cookies от уже решённой капчи.
        "profile_dir": Path.home() / ".cache" / "djangooven" / "kamin-chrome-experiment",
    }
    # print("Обычная цена")
    # result = fetch_html("https://astov.ru/pechikaminy/seriya-alisa/alisa-800/")
    # print(result)
    # time.sleep(4)
    # print("Обычная цена")
    # result = fetch_html("https://www.technolit.ru/production/pechi-dlya-bani/pechi-iskander/iskander-zk-25-p2-pro-uragan/")
    # print(result)
    # time.sleep(4)
    # print("404")
    # result = fetch_html("https://www.technolit.ru/production/pechi-dlya-bani/pechi-iskander/iskander-zk-18-pro-")
    # print(result)



    # print("Обычная цена")
    # result = fetch_html("https://easysteam.ru/products/product/1006259")
    # print(result)
    # time.sleep(4)
    # print("Обычная цена")
    # result = fetch_html("https://easysteam.ru/products/product/1006189")
    # print(result)
    # time.sleep(4)
    # print("404")
    # result = fetch_html("https://easysteam.ru/products/product/990010")
    # print(result)


    # print("Обычная цена")
    # result = fetch_html_playwright("https://prometall.ru/pech-bannaya-eiforiya45-setka")
    # print(result)
    # time.sleep(4)
    # print("цена со скидкой")
    # result = fetch_html_playwright("https://prometall.ru/otopitelno-varochnaya-pech-tayga-pro")
    # print(result)
    # time.sleep(4)
    # print("404")
    # result = fetch_html_playwright("https://prometall.ru/otopitelno-varochnaya-pech-ta")
    # print(result)

    # print("Обычная цена")
    # result = fetch_html_playwright("https://saunaru.com/product/harvia-drovyanaya-pech-wk300ld-legend-300")
    # print(result)
    # time.sleep(4)
    # print("цена со скидкой")
    # result = fetch_html_playwright("https://saunaru.com/product/sawo-blok-moschnosti-dopolnitelnyy-9-kvtsaunova-20-artikul-sau-ps-2")
    # print(result)
    # time.sleep(4)
    # print("Нет в наличии")
    # result = fetch_html_playwright("https://saunaru.com/product/harvia-elektricheskaya-pech-forte-hafb900400s-af9-steel-s-vynosnoy-panelyu-upravleniya")
    # print(result)
    # time.sleep(4)
    # print("404")
    # result = fetch_html_playwright("https://saunaru.com/product/harvia-elektricheskaya-pech-fort-panelyu-upravleniya")
    # print(result)




    # print("Обычная цена")
    # result = fetch_html("https://astov.ru/pechikaminy/seriya-mayolika/mayolika-classic/")
    # print(result)
    # time.sleep(4)
    # print("цена со скидкой")
    # result = fetch_html("https://astov.ru/pechikaminy/seriya-alisa/alisa-800/")
    # print(result)
    # time.sleep(4)
    # print("404")
    # result = fetch_html("https://astov.ru/pechikaminy/seriya-mayolika/mayolika-cl/")
    # print(result)
    # time.sleep(4)




    # print("Обычная цена")
    # result = fetch_html("https://nkamin.ru/catalog/pechi-dlya-bani/aston/12")
    # print(result)
    # time.sleep(4)
    # print("Обычная и скидки")
    # result = fetch_html("https://nkamin.ru/discounts/pechi-dlya-bani/uragan-16-205-v-oblitsovke-izba")
    # print(result)
    # time.sleep(4)
    # print("Есть на заказ все, stock - false")
    # result = fetch_html("https://nkamin.ru/catalog/pechi-dlya-bani/born/fire-60-e")
    # print(result)
    # time.sleep(4)
    # print("Наличие на складе только у 1")
    # result = fetch_html("https://nkamin.ru/catalog/pechi-dlya-bani/aston/shtorm-16-dt-4s-bv")
    # print(result)
    # time.sleep(4)
    # print(404)
    # result = fetch_html("https://nkamin.ru/catalog/pechi-dlya-bani/vezuvij/rusich/rusich-ak-4-bez-baka")
    # print(result)


    test_urls = [
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/chugunnye/pech-stav-tomera/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/metallicheskie/pech_denali_stav/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/metallicheskie/pech-denali-s-stav/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/metallicheskie/pech_denali_lx_stav/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/keramicheskie/pech-denali-lx-top-cr03-stav/",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/keramicheskie/pech-denali-lx-top-cm01-stav/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/chugunnye/pech_trenk_plamen/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/chugunnye/pech_dora_8_n_zelenaya_plamen/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/chugunnye/pech_dora_8_n_chernaya_plamen/#options",
        "https://kamin.ru/katalog/pechi/otopitel_nye_kaminofeny/chugunnye/pech_maestral_n_bezhevaya_plamen/",
    ]
    for index, url in enumerate(test_urls):
        result = fetch_html_playwright(url, **test_browser_options)
        print(result)
        if index < len(test_urls) - 1:
            time.sleep(4)
    #
    # result = fetch_html("https://kamin.ru/katalog/topki/odnostoronnie_ploskoe_steklo/topka_lci_11_gf_liseoci/")
    # print(result)
    # time.sleep(4)
    #
    # result = fetch_html("https://kamin.ru/katalog/topki/odnostoronnie_ploskoe_steklo/topka_rad_305_h_t1_schwarz_abv_92010619_hark/")
    # print(result)
    #
    # time.sleep(4)
    #
    # result = fetch_html("https://kamin.ru/katalog/topki/odnostoronnie_ploskoe_steklo/topka_rad_305_warz_ab2010619_hark/")
    # print(result)

    # result = fetch_html("https://gk-kovcheg.ru/catalog/fireway/chugunnyie-otopitelnyie-pechi/dacha-i.html")
    # print(result)
    # time.sleep(4)
    # result = fetch_html("https://gk-kovcheg.ru/catalog/nmk/kotlyi-dlya-doma/sirius-10.html")
    # print(result)
    # time.sleep(4)
    #
    # result = fetch_html("https://gk-kovcheg.ru/catalog/fireway/bannyie-pechi/parovar-16-kovka-(211).html")
    # print(result)
    # time.sleep(4)
    #
    # result = fetch_html("https://gk-kovcheg.ru/catalog/fireway/pechnoe-lite-pr/pr-02-dvercza-podduvalnaya.html")
    # print(result)

    # print("Обычная цена")
    # result = fetch_html_playwright("https://prometall.ru/pech-bannaya-atmosfera-l-setka-prutok")
    # print(result)
    # time.sleep(4)
    # print("цена со скидкой")
    # result = fetch_html("https://www.ecokamin.ru/catalog/kaminy/myunkhen/14732/")
    # print(result)
