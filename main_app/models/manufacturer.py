from django.db import models

from main_app.services.slug import build_unique_slug


class Manufacturer(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Производитель",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )

    logo = models.ImageField(
        upload_to="manufacturers/",
        verbose_name="Логотип",
    )

    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Приоритет",
        help_text="Чем больше значение — тем выше бренд",
    )

    # --- SEO / контент ---
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Название страницы",
    )

    seo_description = models.TextField(
        blank=True,
        verbose_name="Описание страницы",
    )

    seo_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Ключевые слова",
    )

    description = models.TextField(
        blank=True,
        verbose_name="Полное описание",
    )

    slug = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="ЧПУ (slug)",
    )

    video = models.TextField(
        blank=True,
        verbose_name="Видео",
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
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_value = self.slug or self.name

        if (
            not self.slug
            or Manufacturer.objects.filter(slug=self.slug).exclude(pk=self.pk).exists()
        ):
            self.slug = build_unique_slug(self, slug_value, "manufacturer")

        super().save(*args, **kwargs)


class ManufacturerImage(models.Model):
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Производитель",
    )

    image = models.ImageField(
        upload_to="manufacturer_images/",
        verbose_name="Фото",
    )

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
    )

    class Meta:
        verbose_name = "Фото раздела"
        verbose_name_plural = "Фото разделов"
        ordering = ["ordering"]

    def __str__(self):
        return f"Фото — {self.manufacturer.name}"
