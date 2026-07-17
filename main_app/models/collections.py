from django.db import models

from main_app.models.manufacturer import Manufacturer
from main_app.models.product import Product
from main_app.services.slug import build_unique_slug


class Collection(models.Model):
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        related_name="collections",
        verbose_name="Производитель",
    )

    products = models.ManyToManyField(
        Product,
        related_name="collections",
        blank=True,
        verbose_name="Товары",
    )

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название",
    )

    slug = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="slug (url)",
    )

    # SEO
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

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активность",
    )

    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Приоритет",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-priority", "name"]
        verbose_name = "Коллекция"
        verbose_name_plural = "Коллекции"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_value = self.slug or self.name

        if (
            not self.slug
            or Collection.objects.filter(slug=self.slug).exclude(pk=self.pk).exists()
        ):
            self.slug = build_unique_slug(self, slug_value, "collection")

        super().save(*args, **kwargs)
