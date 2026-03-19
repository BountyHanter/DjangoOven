from django.db import models
from slugify import slugify

from main_app.models.choices import (
    HEATED_VOLUME_CHOICES,
     FIREBOX_MATERIAL_CHOICES,
    FIREBOX_TYPE_CHOICES,
    INSTALLATION_TYPE_CHOICES,
    GLASS_COUNT_CHOICES,
    FIRE_VIEW_CHOICES,
    HEATER_TYPE_CHOICES,
    DOOR_MECHANISM_CHOICES,
    STONE_MATERIAL_CHOICES,
    TANK_TYPE_CHOICES, CHIMNEY_CONNECTION_CHOICES, LINING_MATERIAL_CHOICES, FUEL_TYPE_CHOICES,
)
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
        verbose_name="Slug"
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

    video_url = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео-обзор",
    )

    video_preview = models.ImageField(
        upload_to="products/video_previews/",
        null=True,
        blank=True,
        verbose_name="Превью видео",
    )

    schema = models.FileField(
        null=True,
        blank=True,
        upload_to="products/schema/",
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
        verbose_name="Новинка"
    )

    is_bestseller = models.BooleanField(
        default=False,
        verbose_name="Хит продаж"
    )

    # --- ПАРАМЕТРЫ И ХАРАКТЕРИСТИКИ ---

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

    heated_volume = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Площадь/объём отопления",
    )

    power_kw = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Мощность (кВт)",
    )

    lining_material = models.CharField(
        max_length=32,
        choices=LINING_MATERIAL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Материал футеровки",
    )

    fuel_type = models.CharField(
        max_length=32,
        choices=FUEL_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип топлива",
    )

    firebox_material = models.CharField(
        max_length=32,
        choices=FIREBOX_MATERIAL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Материал печи",
    )


    firebox_type = models.CharField(
        max_length=32,
        choices=FIREBOX_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Вид топки",
    )

    installation_type = models.CharField(
        max_length=32,
        choices=INSTALLATION_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип установки",
    )

    glass_count = models.CharField(
        max_length=32,
        choices=GLASS_COUNT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Количество стекол",
    )

    fire_view = models.CharField(
        max_length=32,
        choices=FIRE_VIEW_CHOICES,
        null=True,
        blank=True,
        verbose_name="Обзор огня",
    )

    heater_type = models.CharField(
        max_length=32,
        choices=HEATER_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Каменка",
    )

    water_circuit = models.BooleanField(
        default=False,
        verbose_name="Водяной контур",
    )

    stone_material = models.CharField(
        max_length=32,
        choices=STONE_MATERIAL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Материал камня",
    )

    tank_type = models.CharField(
        max_length=32,
        choices=TANK_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип бака",
    )

    door_mechanism = models.CharField(
        max_length=32,
        choices=DOOR_MECHANISM_CHOICES,
        null=True,
        blank=True,
        verbose_name="Механизм открывания двери",
    )

    chimney_diameter = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Диаметр дымохода",
    )

    chimney_connection = models.CharField(
        max_length=16,
        choices=CHIMNEY_CONNECTION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Подключение к дымоходу",
    )

    dimensions = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Габариты (Г*Ш*В, мм)",
        help_text="Формат: Г*Ш*В в мм",
    )

    weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Вес, кг",
    )

    steam_volume_from = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Объём парной от, м³",
    )

    steam_volume_to = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Объём парной до, м³",
    )

    stone_weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Масса закладываемых камней, кг",
    )

    closed_heater_volume = models.PositiveIntegerField(
        verbose_name="Объём закрытой каменки (л)",
        blank=True,
        null=True,
    )

    warranty_years = models.PositiveIntegerField(
        verbose_name="Гарантия (лет)",
        blank=True,
        null=True,
    )

    efficiency = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="КПД (%)",
        blank=True,
        null=True,
    )

    long_fire = models.BooleanField(
        default=False,
        verbose_name="Длительное горение"
    )

    heat_exchanger = models.BooleanField(
        default=False,
        verbose_name="Теплообменник",
    )

    glass_lift = models.BooleanField(
        default=False,
        verbose_name="Подъём стекла",
    )

    damper = models.BooleanField(
        default=False,
        verbose_name="Шибер",
    )

    cooking_panel = models.BooleanField(
        default=False,
        verbose_name="Варочная панель",
    )

    oven_weight = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Вес печи, кг",
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

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


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


class ProductDocument(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="documents",
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