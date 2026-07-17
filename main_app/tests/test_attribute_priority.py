import pytest
from django.core.exceptions import ValidationError

from main_app.models import ProductAttribute, ProductAttributeOption


@pytest.mark.django_db
def test_attribute_priority_zero_can_repeat():
    ProductAttribute.objects.create(
        name="First",
        type=ProductAttribute.AttributeType.TEXT,
    )
    attribute = ProductAttribute.objects.create(
        name="Second",
        type=ProductAttribute.AttributeType.TEXT,
    )

    assert attribute.priority == 0


@pytest.mark.django_db
def test_attribute_positive_priority_must_be_unique():
    ProductAttribute.objects.create(
        name="First",
        type=ProductAttribute.AttributeType.TEXT,
        priority=1,
    )

    with pytest.raises(ValidationError):
        ProductAttribute.objects.create(
            name="Second",
            type=ProductAttribute.AttributeType.TEXT,
            priority=1,
        )


@pytest.mark.django_db
def test_attribute_option_priority_zero_can_repeat_inside_attribute():
    attribute = ProductAttribute.objects.create(
        name="Material",
        type=ProductAttribute.AttributeType.CHOICE,
    )

    ProductAttributeOption.objects.create(attribute=attribute, value="First")
    option = ProductAttributeOption.objects.create(
        attribute=attribute,
        value="Second",
    )

    assert option.priority == 0


@pytest.mark.django_db
def test_attribute_option_positive_priority_must_be_unique_inside_attribute():
    attribute = ProductAttribute.objects.create(
        name="Material",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    other_attribute = ProductAttribute.objects.create(
        name="Fuel",
        type=ProductAttribute.AttributeType.CHOICE,
    )

    ProductAttributeOption.objects.create(
        attribute=attribute,
        value="First",
        priority=1,
    )
    ProductAttributeOption.objects.create(
        attribute=other_attribute,
        value="Other",
        priority=1,
    )

    with pytest.raises(ValidationError):
        ProductAttributeOption.objects.create(
            attribute=attribute,
            value="Second",
            priority=1,
        )
