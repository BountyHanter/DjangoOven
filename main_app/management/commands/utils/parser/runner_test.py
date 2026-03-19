import time

import httpx
from playwright.sync_api import sync_playwright

from main_app.management.commands.utils.parser.config import HEADERS
from main_app.management.commands.utils.parser.extractors import get_extractor
from main_app.management.commands.utils.parser.schemas import FetchResult


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
                answer.status_code = status_code
                answer.error_text = f"extract_error: {e}"
                return answer
        else:
            # если extractor не найден — это твоя ошибка конфигурации
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

def fetch_html(url: str) -> FetchResult:
    try:
        # обычный HTTP-запрос (быстро и дёшево)
        with httpx.Client(
            timeout=30,
            headers=HEADERS,
        ) as client:
            response = client.get(url)

        return build_result(
            url=url,
            status_code=response.status_code,
            html=response.text,
            error_text=response.reason_phrase,
        )

    except Exception as e:
        # любая ошибка сети / таймаут / DNS
        return build_result(
            url=url,
            status_code=None,
            html=None,
            error_text=str(e),
        )
def fetch_html_playwright(url: str) -> FetchResult:
    try:
        # браузер для сложных сайтов (JS, защита и тд)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            context = browser.new_context(
                user_agent=HEADERS["User-Agent"],
                extra_http_headers={
                    "Accept": HEADERS["Accept"],
                    "Accept-Language": HEADERS["Accept-Language"],
                }
            )

            page = context.new_page()

            # ждём полной загрузки страницы
            response = page.goto(url, wait_until="load")

            status_code = response.status if response else None
            html = page.content()

            browser.close()

        return build_result(
            url=url,
            status_code=status_code,
            html=html,
            error_text=None,
        )

    except Exception as e:
        return build_result(
            url=url,
            status_code=None,
            html=None,
            error_text=str(e),
        )

if __name__ == "__main__":
    print("Обычная цена")
    result = fetch_html("https://astov.ru/pechikaminy/seriya-alisa/alisa-800/")
    print(result)
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


    # result = fetch_html("https://kamin.ru/katalog/kaminy_oblicovki/vstroennye/vstavka_vert_dlya_dromond_cr_90_edilkamin/")
    # print(result)
    # time.sleep(4)
    # result = fetch_html("https://kamin.ru/katalog/topki/odnostoronnie_ploskoe_steklo/topka_f_750_w_stav/")
    # print(result)
    # time.sleep(4)
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
