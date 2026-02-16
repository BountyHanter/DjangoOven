from django.db import models
from slugify import slugify

from main_app.models.choices import MATERIAL_CHOICES, FIREBOX_MATERIAL_CHOICES, STONE_MATERIAL_CHOICES, \
    DOOR_TYPE_CHOICES, DOOR_MECHANISM_CHOICES, FIRE_VIEW_CHOICES, GLASS_COUNT_CHOICES, FUEL_TYPE_CHOICES, \
    TANK_TYPE_CHOICES, FIREBOX_TYPE_CHOICES, STONE_TYPE_CHOICES, WATER_HEATING_CHOICES, PLACEMENT_CHOICES, \
    FACING_TYPE_CHOICES
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
        blank=True,
        verbose_name="Разделы",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
    )

    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео-обзор",
    )

    # --- ЦЕНЫ ---
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Обычная цена",
    )

    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
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

    is_discount = models.BooleanField(
        default=False,
        verbose_name="Скидка"
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

    dimensions = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Размеры товара",
        help_text="Формат: ДxШxВ в мм",
    )

    weight = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Вес товара (кг)",
    )

    heated_volume = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Объём отапливаемого помещения",
    )

    steam_volume_from = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Объём парильного помещения, от",
    )

    steam_volume_to = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Объём парильного помещения, до",
    )

    chimney_diameter = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Диаметр дымохода (мм)",
    )

    power_kw = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Мощность (кВт)",
    )

    stone_weight = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Масса закладываемых камней"
    )

    material = models.CharField(
        max_length=32,
        choices=MATERIAL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Вид топки",
    )

    firebox_material = models.CharField(
        max_length=32,
        choices=FIREBOX_MATERIAL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Материал топки",
    )

    stone_material = models.CharField(
        max_length=32,
        choices=STONE_MATERIAL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Материал камня",
    )

    door_type = models.CharField(
        max_length=32,
        choices=DOOR_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Дверца",
    )

    door_mechanism = models.CharField(
        max_length=32,
        choices=DOOR_MECHANISM_CHOICES,
        blank=True,
        null=True,
        verbose_name="Механизм открывания дверцы",
    )

    fire_view = models.CharField(
        max_length=32,
        choices=FIRE_VIEW_CHOICES,
        blank=True,
        null=True,
        verbose_name="Обзор огня",
    )

    glass_count = models.CharField(
        max_length=32,
        choices=GLASS_COUNT_CHOICES,
        blank=True,
        null=True,
        verbose_name="Количество стекол",
    )

    fuel_type = models.CharField(
        max_length=32,
        choices=FUEL_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип топлива",
    )

    tank_type = models.CharField(
        max_length=32,
        choices=TANK_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип бака",
    )

    firebox_type = models.CharField(
        max_length=32,
        choices=FIREBOX_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Вид топки",
    )

    stone_type = models.CharField(
        max_length=32,
        choices=STONE_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Каменка",
    )

    water_heating = models.CharField(
        max_length=32,
        choices=WATER_HEATING_CHOICES,
        null=True,
        blank=True,
        verbose_name="Нагрев воды",
    )

    placement = models.CharField(
        max_length=32,
        choices=PLACEMENT_CHOICES,
        null=True,
        blank=True,
        verbose_name="Расположение топки",
    )

    facing_type = models.CharField(
        max_length=32,
        choices=FACING_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name="Тип облицовки",
    )

    heat_exchanger = models.BooleanField(
        default=False,
        verbose_name="Теплообменник",
    )

    long_burning = models.BooleanField(
        default=False,
        verbose_name="Система длительного горения",
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
