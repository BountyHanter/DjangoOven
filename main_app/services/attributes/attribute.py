from django.core.exceptions import ValidationError
from slugify import slugify


def _build_unique_slug(value, fallback, max_length, queryset):
    base_slug = slugify(value) or fallback
    base_slug = base_slug[:max_length]
    slug = base_slug
    counter = 1

    while queryset.filter(slug=slug).exists():
        suffix = f"-{counter}"
        slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
        counter += 1

    return slug


def validate_attribute(attribute):
    from main_app.models.attribute import ProductAttribute

    if (
        attribute.allow_multiple
        and attribute.type != ProductAttribute.AttributeType.CHOICE
    ):
        raise ValidationError(
            {
                "allow_multiple": (
                    "Несколько значений разрешены только для типа "
                    "'Выбор из списка'"
                )
            }
        )


def generate_attribute_slug(attribute):
    from main_app.models.attribute import ProductAttribute

    max_length = attribute._meta.get_field("slug").max_length
    queryset = ProductAttribute.objects.exclude(pk=attribute.pk)

    return _build_unique_slug(
        value=attribute.slug or attribute.name,
        fallback="attribute",
        max_length=max_length,
        queryset=queryset,
    )


def validate_attribute_option(option):
    if not option.attribute_id:
        return

    from main_app.models.attribute import ProductAttribute

    attribute_type = (
        ProductAttribute.objects.filter(pk=option.attribute_id)
        .values_list("type", flat=True)
        .first()
    )

    if attribute_type and attribute_type != ProductAttribute.AttributeType.CHOICE:
        raise ValidationError(
            {
                "attribute": (
                    "Варианты можно добавлять только для характеристик "
                    "типа 'Выбор из списка'"
                )
            }
        )


def generate_attribute_option_slug(option):
    from main_app.models.attribute import ProductAttributeOption

    max_length = option._meta.get_field("slug").max_length

    if not option.attribute_id:
        return _build_unique_slug(
            value=option.slug or option.value,
            fallback="option",
            max_length=max_length,
            queryset=ProductAttributeOption.objects.none(),
        )

    queryset = ProductAttributeOption.objects.filter(
        attribute_id=option.attribute_id,
    ).exclude(pk=option.pk)

    return _build_unique_slug(
        value=option.slug or option.value,
        fallback="option",
        max_length=max_length,
        queryset=queryset,
    )


def get_attribute_value_display(attribute_value):
    if attribute_value.option_id:
        return attribute_value.option.value

    if attribute_value.value_number is not None:
        if attribute_value.attribute_id and attribute_value.attribute.unit:
            return f"{attribute_value.value_number} {attribute_value.attribute.unit}"
        return str(attribute_value.value_number)

    if attribute_value.value_bool is not None:
        return "Да" if attribute_value.value_bool else "Нет"

    return attribute_value.value_text


def validate_attribute_value(attribute_value):
    from main_app.models.attribute import (
        ProductAttribute,
        ProductAttributeOption,
        ProductAttributeValue,
    )

    errors = {}
    attribute = None

    if attribute_value.attribute_id:
        attribute = (
            ProductAttribute.objects.filter(pk=attribute_value.attribute_id)
            .only("type", "allow_multiple")
            .first()
        )

    if attribute_value.option_id and attribute_value.attribute_id:
        option_attribute_id = (
            ProductAttributeOption.objects.filter(pk=attribute_value.option_id)
            .values_list("attribute_id", flat=True)
            .first()
        )

        if (
            option_attribute_id is not None
            and option_attribute_id != attribute_value.attribute_id
        ):
            errors["option"] = (
                "Выбранный вариант не относится к выбранной характеристике"
            )

    if (
        attribute
        and attribute_value.product_id
        and not attribute.allow_multiple
    ):
        exists = ProductAttributeValue.objects.filter(
            product_id=attribute_value.product_id,
            attribute_id=attribute_value.attribute_id,
        ).exclude(pk=attribute_value.pk).exists()

        if exists:
            errors["attribute"] = (
                "У этой характеристики для товара уже есть значение"
            )

    if not attribute:
        if errors:
            raise ValidationError(errors)
        return

    _validate_value_by_attribute_type(attribute_value, attribute.type, errors)

    if errors:
        raise ValidationError(errors)


def _validate_value_by_attribute_type(attribute_value, attribute_type, errors):
    from main_app.models.attribute import ProductAttribute

    values = {
        "option": attribute_value.option_id is not None,
        "value_text": bool((attribute_value.value_text or "").strip()),
        "value_number": attribute_value.value_number is not None,
        "value_bool": attribute_value.value_bool is not None,
    }
    rules = {
        ProductAttribute.AttributeType.CHOICE: (
            "option",
            "Для характеристики типа 'Выбор из списка' нужно выбрать вариант",
            "Для характеристики типа 'Выбор из списка' используется только вариант",
        ),
        ProductAttribute.AttributeType.NUMBER: (
            "value_number",
            "Для числовой характеристики нужно указать число",
            "Для числовой характеристики используется только число",
        ),
        ProductAttribute.AttributeType.BOOLEAN: (
            "value_bool",
            "Для характеристики Да/Нет нужно указать значение",
            "Для характеристики Да/Нет используется только boolean-значение",
        ),
        ProductAttribute.AttributeType.TEXT: (
            "value_text",
            "Для текстовой характеристики нужно указать текст",
            "Для текстовой характеристики используется только текст",
        ),
    }

    required_field, required_error, extra_error = rules.get(
        attribute_type,
        (None, None, None),
    )
    if not required_field:
        return

    if not values[required_field]:
        errors[required_field] = required_error

    for field, has_value in values.items():
        if field != required_field and has_value:
            errors[field] = extra_error
