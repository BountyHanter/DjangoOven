from django.db import models


class Review(models.Model):
    client_name = models.CharField(
        max_length=255,
        verbose_name="Клиент",
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Локация",
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Стоимость",
    )

    video_url = models.URLField(
        blank=True,
        verbose_name="Ссылка на видео",
    )

    installation_time = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Время затраченное на монтаж",
    )

    work_description = models.TextField(
        verbose_name="Произведённые работы",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.client_name
