from django.db import models

from main_app.models import Product


class ParserResult(models.Model):

    class Status(models.IntegerChoices):
        OK = 200, "Успешно"
        REDIRECT = 301, "Редирект (возможно ошибка)"
        BAD_REQUEST = 400, "Некорректный запрос"
        FORBIDDEN = 403, "Доступ запрещён / антибот"
        NOT_FOUND = 404, "Страница не найдена"
        TIMEOUT = 408, "Таймаут запроса"
        TOO_MANY_REQUESTS = 429, "Слишком много запросов"
        SERVER_ERROR = 500, "Ошибка сервера"
        BAD_GATEWAY = 502, "Плохой шлюз"
        SERVICE_UNAVAILABLE = 503, "Сервис недоступен"
        GATEWAY_TIMEOUT = 504, "Таймаут шлюза"

    url = models.URLField("Ссылка")

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="parser",
        verbose_name="Товар",
    )

    status = models.IntegerField(
        "Статус парсинга",
        choices=Status,
        null=True,
        blank=True,
    )

    error_text = models.TextField(
        "Текст ошибки",
        blank=True,
        null=True,
    )

    processing_time = models.DurationField(
        "Время обработки",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.url} — {self.get_status_display()}"

    class Meta:
        verbose_name = "Парсинг"
        verbose_name_plural = "Парсинги"
