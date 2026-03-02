from django.db import models
from slugify import slugify

from main_app.models.choices import (
    PURPOSE_CHOICES,
    FUEL_TYPE_CHOICES,
    HEATED_VOLUME_CHOICES,
    STEAM_ROOM_VOLUME_CHOICES,
    POWER_KW_CHOICES,
    FIREBOX_MATERIAL_CHOICES,
    FIREBOX_TYPE_CHOICES,
    INSTALLATION_TYPE_CHOICES,
    FIREBOX_ORIENTATION_CHOICES,
    COMBUSTION_TYPE_CHOICES,
    GLASS_COUNT_CHOICES,
    FIRE_VIEW_CHOICES,
    CLADDING_MATERIAL_CHOICES,
    HEATER_TYPE_CHOICES,
    DOOR_MECHANISM_CHOICES,
    CHIMNEY_DIAMETER_CHOICES,
    STONE_MATERIAL_CHOICES,
    TANK_TYPE_CHOICES, CHIMNEY_CONNECTION_CHOICES,
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

    video_url = models.CharField(
        max_length=512,
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

    # --- ЦЕНЫ ---
    price = models.PositiveIntegerField(
        verbose_name="Обычная цена",
    )

    discount_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Цена со скидкой",
    )

    price_in_euro = models.BooleanField(
        default=False,
        verbose_name="Цена в евро",
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

    is_popular = models.BooleanField(
        default=False,
        verbose_name="Популярный товар"
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

    purpose = models.CharField(
        max_length=32,
        choices=PURPOSE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Назначение",
    )

    fuel_type = models.CharField(
        max_length=32,
        choices=FUEL_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип топлива",
    )

    heated_volume = models.CharField(
        max_length=32,
        choices=HEATED_VOLUME_CHOICES,
        null=True,
        blank=True,
        verbose_name="Площадь/объём отопления",
    )

    steam_room_volume = models.CharField(
        max_length=32,
        choices=STEAM_ROOM_VOLUME_CHOICES,
        null=True,
        blank=True,
        verbose_name="Площадь/объём парной",
    )

    power_kw = models.CharField(
        max_length=32,
        choices=POWER_KW_CHOICES,
        null=True,
        blank=True,
        verbose_name="Мощность (кВт)",
    )

    firebox_material = models.CharField(
        max_length=32,
        choices=FIREBOX_MATERIAL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Материал топки",
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

    firebox_orientation = models.CharField(
        max_length=32,
        choices=FIREBOX_ORIENTATION_CHOICES,
        null=True,
        blank=True,
        verbose_name="Ориентация топки",
    )

    combustion_type = models.CharField(
        max_length=32,
        choices=COMBUSTION_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип горения",
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

    cladding_material = models.CharField(
        max_length=32,
        choices=CLADDING_MATERIAL_CHOICES,
        null=True,
        blank=True,
        verbose_name="Материал облицовки",
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
        max_length=32,
        choices=CHIMNEY_DIAMETER_CHOICES,
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
        verbose_name="Габариты (Д×Ш×В, мм)",
        help_text="Формат: ДxШxВ в мм",
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

    efficiency = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="КПД, %",
        help_text="Указывается в процентах",
    )

    warranty_years = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Гарантия, лет",
    )

    closed_heater_volume = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Объём закрытой каменки, л",
    )

    package_weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Масса в упаковке, кг",
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