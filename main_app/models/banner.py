from django.db import models

from main_app.models import Section, Manufacturer


class Banner(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )

    image = models.ImageField(
        upload_to="banners/",
        verbose_name="Картинка",
    )

    sections = models.ManyToManyField(
        Section,
        blank=True,
        verbose_name="Разделы",
        help_text="Если не выбрано — показывается во всех разделах",
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Бренд",
        help_text="Если выбран — баннер показывается только в бренде",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создан",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлён",
    )

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return self.title