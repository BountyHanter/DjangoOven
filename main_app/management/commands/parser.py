import time
import random
from collections import defaultdict, deque
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.utils import timezone

from main_app.management.commands.utils.parser.apply_result import apply_parser_result
from main_app.management.commands.utils.parser.runner_test import fetch_html_playwright, fetch_html
from main_app.models.parser import ParserResult
from main_app.management.commands.utils.parser.config import PLAYWRIGHT_DOMAINS


# -----------------------------
# очередь по доменам
# -----------------------------
def get_parser_queue():
    qs = ParserResult.objects.only("id", "url")

    groups = defaultdict(deque)

    for obj in qs:
        domain = urlparse(obj.url).netloc.replace("www.", "")
        groups[domain].append(obj)

    # рандом внутри домена
    for domain in groups:
        items = list(groups[domain])
        random.shuffle(items)
        groups[domain] = deque(items)

    result = []

    while groups:
        empty = []

        for domain, items in list(groups.items()):
            if items:
                result.append(items.popleft())

            if not items:
                empty.append(domain)

        for domain in empty:
            del groups[domain]

    return result


# -----------------------------
# выбор fetcher
# -----------------------------
def get_fetcher(url: str):
    domain = urlparse(url).netloc.replace("www.", "")

    if domain in PLAYWRIGHT_DOMAINS:
        return fetch_html_playwright

    return fetch_html


# -----------------------------
# delay (~30 сек среднее)
# -----------------------------
def get_delay() -> float:
    # 10% шанс длинной паузы
    if random.random() < 0.1:
        return random.uniform(60, 120)

    # нормальное распределение
    delay = random.normalvariate(30, 10)
    return max(5.0, delay)

# -----------------------------
# команда
# -----------------------------
class Command(BaseCommand):
    help = "Run parser with domain queue and smart delays"

    def handle(self, *args, **options):
        parser_queue = get_parser_queue()

        self.stdout.write(f"Всего URL: {len(parser_queue)}")

        for i, obj in enumerate(parser_queue, start=1):
            url = obj.url
            domain = urlparse(url).netloc.replace("www.", "")

            fetcher = get_fetcher(url)

            self.stdout.write("=" * 80)
            self.stdout.write(f"[{i}] Обработка: {url}")
            self.stdout.write(f"Домен: {domain}")
            self.stdout.write(f"Фетчер: {fetcher.__name__}")

            result = fetcher(url)

            self.stdout.write(f"Статус: {result.status_code}")

            if result.data:
                self.stdout.write(f"Данные: {result.data}")
            else:
                self.stdout.write(f"Ошибка: {result.error_text}")

            try:
                apply_parser_result(obj, result)
                self.stdout.write("Сохранено в БД")

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка сохранения: {e}"))

                # фиксируем в БД что была ошибка
                obj.status = ParserResult.Status.SERVER_ERROR
                obj.error_text = str(e)
                obj.processing_time = timezone.now()
                obj.save(update_fields=["status", "error_text", "processing_time"])

            delay = get_delay()
            self.stdout.write(f"Пауза: {delay:.2f} сек")

            time.sleep(delay)