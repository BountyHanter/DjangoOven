from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from slugify import slugify


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
        if self.allow_multiple and self.type != self.AttributeType.CHOICE:
            raise ValidationError(
                {
                    "allow_multiple": (
                        "Несколько значений разрешены только для типа "
                        "'Выбор из списка'"
                    )
                }
            )

    def _generate_unique_slug(self):
        max_length = self._meta.get_field("slug").max_length
        base_slug = slugify(self.name) or "attribute"
        base_slug = base_slug[:max_length]
        slug = base_slug
        counter = 1

        queryset = ProductAttribute.objects.exclude(pk=self.pk)

        while queryset.filter(slug=slug).exists():
            suffix = f"-{counter}"
            slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
            counter += 1

        return slug

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
        if not self.attribute_id:
            return

        attribute_type = (
            ProductAttribute.objects.filter(pk=self.attribute_id)
            .values_list("type", flat=True)
            .first()
        )

        if (
            attribute_type
            and attribute_type != ProductAttribute.AttributeType.CHOICE
        ):
            raise ValidationError(
                {
                    "attribute": (
                        "Варианты можно добавлять только для характеристик "
                        "типа 'Выбор из списка'"
                    )
                }
            )

    def _generate_unique_slug(self):
        max_length = self._meta.get_field("slug").max_length
        base_slug = slugify(self.value) or "option"
        base_slug = base_slug[:max_length]
        slug = base_slug
        counter = 1

        queryset = ProductAttributeOption.objects.filter(
            attribute_id=self.attribute_id,
        ).exclude(pk=self.pk)

        while self.attribute_id and queryset.filter(slug=slug).exists():
            suffix = f"-{counter}"
            slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
            counter += 1

        return slug

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
        if self.option_id:
            return self.option.value

        if self.value_number is not None:
            if self.attribute_id and self.attribute.unit:
                return f"{self.value_number} {self.attribute.unit}"
            return str(self.value_number)

        if self.value_bool is not None:
            return "Да" if self.value_bool else "Нет"

        return self.value_text

    def clean(self):
        errors = {}
        attribute = None

        if self.attribute_id:
            attribute = (
                ProductAttribute.objects.filter(pk=self.attribute_id)
                .only("type", "allow_multiple")
                .first()
            )

        if self.option_id and self.attribute_id:
            option_attribute_id = (
                ProductAttributeOption.objects.filter(pk=self.option_id)
                .values_list("attribute_id", flat=True)
                .first()
            )

            if (
                option_attribute_id is not None
                and option_attribute_id != self.attribute_id
            ):
                errors["option"] = (
                    "Выбранный вариант не относится к выбранной характеристике"
                )

        if (
            attribute
            and self.product_id
            and not attribute.allow_multiple
        ):
            exists = ProductAttributeValue.objects.filter(
                product_id=self.product_id,
                attribute_id=self.attribute_id,
            ).exclude(pk=self.pk).exists()

            if exists:
                errors["attribute"] = (
                    "У этой характеристики для товара уже есть значение"
                )

        if not attribute:
            if errors:
                raise ValidationError(errors)
            return

        attribute_type = attribute.type
        has_option = self.option_id is not None
        has_text = bool((self.value_text or "").strip())
        has_number = self.value_number is not None
        has_bool = self.value_bool is not None

        if attribute_type == ProductAttribute.AttributeType.CHOICE:
            if not has_option:
                errors["option"] = (
                    "Для характеристики типа 'Выбор из списка' нужно выбрать вариант"
                )

            if has_text:
                errors["value_text"] = (
                    "Для характеристики типа 'Выбор из списка' используется только вариант"
                )
            if has_number:
                errors["value_number"] = (
                    "Для характеристики типа 'Выбор из списка' используется только вариант"
                )
            if has_bool:
                errors["value_bool"] = (
                    "Для характеристики типа 'Выбор из списка' используется только вариант"
                )

        elif attribute_type == ProductAttribute.AttributeType.NUMBER:
            if not has_number:
                errors["value_number"] = (
                    "Для числовой характеристики нужно указать число"
                )

            if has_option:
                errors["option"] = (
                    "Для числовой характеристики используется только число"
                )
            if has_text:
                errors["value_text"] = (
                    "Для числовой характеристики используется только число"
                )
            if has_bool:
                errors["value_bool"] = (
                    "Для числовой характеристики используется только число"
                )

        elif attribute_type == ProductAttribute.AttributeType.BOOLEAN:
            if not has_bool:
                errors["value_bool"] = (
                    "Для характеристики Да/Нет нужно указать значение"
                )

            if has_option:
                errors["option"] = (
                    "Для характеристики Да/Нет используется только boolean-значение"
                )
            if has_text:
                errors["value_text"] = (
                    "Для характеристики Да/Нет используется только boolean-значение"
                )
            if has_number:
                errors["value_number"] = (
                    "Для характеристики Да/Нет используется только boolean-значение"
                )

        elif attribute_type == ProductAttribute.AttributeType.TEXT:
            if not has_text:
                errors["value_text"] = (
                    "Для текстовой характеристики нужно указать текст"
                )

            if has_option:
                errors["option"] = (
                    "Для текстовой характеристики используется только текст"
                )
            if has_number:
                errors["value_number"] = (
                    "Для текстовой характеристики используется только текст"
                )
            if has_bool:
                errors["value_bool"] = (
                    "Для текстовой характеристики используется только текст"
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
