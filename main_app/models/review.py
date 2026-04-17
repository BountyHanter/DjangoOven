from django.db import models

from main_app.models import Product


class Review(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name="Название"
    )

    client_name = models.CharField(
        max_length=255,
        verbose_name="Клиент",
    )

    installation_time = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Время затраченное на монтаж",
    )

    location = models.CharField(
        max_length=255,
        verbose_name="Локация",
    )

    work_description = models.TextField(
        verbose_name="Что сделано",
    )

    price = models.IntegerField(
        verbose_name="Стоимость",
    )

    video_url = models.TextField(
        verbose_name="Ссылка на видео",
    )

    preview_image = models.ImageField(
        upload_to="reviews/video_preview/",
        null=True,
        blank=True,
        verbose_name="Превью видео",
        help_text="Картинка, отображаемая как превью видео"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Продукт"
    )

    date = models.DateField(
        verbose_name="Дата монтажа",
        null=True,
        blank=True,
    )


    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return self.client_name
