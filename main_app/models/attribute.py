from django.db import models
from django.db.models import Q

from main_app.services.attributes.attribute import (
    generate_attribute_option_slug,
    generate_attribute_slug,
    get_attribute_value_display,
    validate_attribute,
    validate_attribute_option,
    validate_attribute_value,
)


class ProductAttribute(models.Model):
    class AttributeType(models.TextChoices):
        CHOICE = "choice", "Выбор из списка"
        BOOLEAN = "boolean", "Да/Нет"
        NUMBER = "number", "Число"
        TEXT = "text", "Текст"

    name = models.CharField(
        max_length=255,
        verbose_name="Название характеристики",
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=True,
        verbose_name="Slug",
    )

    type = models.CharField(
        max_length=32,
        choices=AttributeType.choices,
        verbose_name="Тип характеристики",
    )

    allow_multiple = models.BooleanField(
        default=False,
        verbose_name="Можно несколько значений",
        help_text="Имеет смысл в первую очередь для характеристик типа 'Выбор из списка'",
    )

    unit = models.CharField(
        max_length=32,
        blank=True,
        verbose_name="Единица измерения",
        help_text="Например: кг, кВт, м³, мм",
    )

    class Meta:
        verbose_name = "Характеристика товара"
        verbose_name_plural = "Характеристики товаров"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["type"]),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        validate_attribute(self)

    def _generate_unique_slug(self):
        return generate_attribute_slug(self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()

        self.full_clean()
        super().save(*args, **kwargs)


class ProductAttributeOption(models.Model):
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name="Характеристика",
    )

    value = models.CharField(
        max_length=255,
        verbose_name="Значение",
    )

    slug = models.SlugField(
        max_length=255,
        db_index=True,
        blank=True,
        verbose_name="Slug",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
    )

    class Meta:
        verbose_name = "Вариант характеристики"
        verbose_name_plural = "Варианты характеристик"
        ordering = ["attribute__name", "value"]
        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "slug"],
                name="unique_attribute_option_slug",
            ),
            models.UniqueConstraint(
                fields=["attribute", "value"],
                name="unique_attribute_option_value",
            ),
        ]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        if self.attribute_id:
            return f"{self.attribute.name}: {self.value}"
        return self.value

    def clean(self):
        validate_attribute_option(self)

    def _generate_unique_slug(self):
        return generate_attribute_option_slug(self)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()

        self.full_clean()
        super().save(*args, **kwargs)


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name="Товар",
    )

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="product_values",
        verbose_name="Характеристика",
    )

    option = models.ForeignKey(
        ProductAttributeOption,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="product_values",
        verbose_name="Вариант значения",
    )

    value_text = models.TextField(
        blank=True,
        verbose_name="Текстовое значение",
    )

    value_number = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Числовое значение",
    )

    value_bool = models.BooleanField(
        null=True,
        blank=True,
        verbose_name="Да/Нет",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    class Meta:
        verbose_name = "Значение характеристики товара"
        verbose_name_plural = "Значения характеристик товаров"
        indexes = [
            models.Index(fields=["product", "attribute"]),
            models.Index(fields=["attribute", "option"]),
            models.Index(fields=["value_number"]),
            models.Index(fields=["value_bool"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "attribute", "option"],
                condition=Q(option__isnull=False),
                name="unique_product_attribute_option",
            ),
            models.UniqueConstraint(
                fields=["product", "attribute"],
                condition=Q(option__isnull=True),
                name="unique_product_attribute_scalar_value",
            ),
        ]

    def __str__(self):
        product_name = self.product.name if self.product_id else "Товар"
        attribute_name = (
            self.attribute.name if self.attribute_id else "характеристика"
        )
        return f"{product_name} — {attribute_name}: {self.display_value}"

    @property
    def display_value(self):
        return get_attribute_value_display(self)

    def clean(self):
        validate_attribute_value(self)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
