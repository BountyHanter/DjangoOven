from django.db import models
from django.core.validators import MinValueValidator
from slugify import slugify

from main_app.models.manufacturer import Manufacturer
from main_app.models.section import Section


class Product(models.Model):
    # --- ОСНОВНАЯ ИНФОРМАЦИЯ ---
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование",
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name="Slug",
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Производитель",
    )

    sections = models.ManyToManyField(
        Section,
        verbose_name="Разделы",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
    )

    schema = models.FileField(
        upload_to="products/schema/",
        null=True,
        blank=True,
        verbose_name="Схема (формат pdf)",
    )

    # --- ЦЕНЫ ---
    price = models.PositiveIntegerField(
        verbose_name="Обычная цена",
    )

    discount_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Цена со скидкой",
    )

    # --- СТАТУСЫ ---
    free_delivery = models.BooleanField(
        default=False,
        verbose_name="Бесплатная доставка",
    )

    in_stock = models.BooleanField(
        default=True,
        verbose_name="В наличии на складе",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен в каталоге",
    )

    is_new = models.BooleanField(
        default=False,
        verbose_name="Новинка",
    )

    is_bestseller = models.BooleanField(
        default=False,
        verbose_name="Хит продаж",
    )

    # --- ПАРАМЕТРЫ И ХАРАКТЕРИСТИКИ ---

    priority = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name="Приоритет",
        help_text="1 — самый высокий приоритет; пустое значение — без приоритета",
    )

    sku = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Артикул(ы)",
        help_text="Можно хранить через запятую",
    )

    series = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Серия товара",
    )

    # --- SEO ---
    seo_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Название страницы товара",
    )

    seo_description = models.TextField(
        blank=True,
        verbose_name="Описание страницы товара",
    )

    seo_keywords = models.TextField(
        blank=True,
        verbose_name="Ключевые слова товара",
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
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["in_stock"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug or self.slug.strip() == "":
            base_slug = slugify(self.name) or "product"
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name) or "product"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="products/images/",
        verbose_name="Изображение",
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name="Главное изображение",
    )

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
    )

    class Meta:
        ordering = ["ordering"]
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"

    def __str__(self):
        return f"Изображение — {self.product.name}"


class ProductVideo(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="videos",
    )

    preview_url = models.URLField(
        max_length=500,
        verbose_name="Ссылка на превью",
        null=True,
        blank=True,
    )

    url = models.URLField(
        max_length=500,
        verbose_name="Ссылка на видео",
    )

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
    )

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = "Видео товара"
        verbose_name_plural = "Видео товара"

    def __str__(self):
        return self.url


class ProductDocument(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Товар",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Название документа",
    )

    file = models.FileField(
        upload_to="products/documents/",
        verbose_name="Файл",
    )

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок",
    )

    class Meta:
        ordering = ["ordering"]
        verbose_name = "Документ товара"
        verbose_name_plural = "Документы товара"

    def __str__(self):
        return self.title
