import pytest

from main_app.models import (
    Collection,
    Manufacturer,
    Product,
    ProductAttribute,
    ProductAttributeOption,
    Section,
)


@pytest.mark.django_db
def test_product_slug_is_generated_unique():
    Product.objects.create(name="Same Product", price=100)
    product = Product.objects.create(name="Same Product", price=100)

    assert product.slug == "same-product-1"


@pytest.mark.django_db
def test_product_duplicate_manual_slug_is_made_unique():
    Product.objects.create(name="First Product", slug="custom", price=100)
    product = Product.objects.create(name="Second Product", slug="custom", price=100)

    assert product.slug == "custom-1"


@pytest.mark.django_db
def test_section_slug_is_generated_unique():
    Section.objects.create(name="Same Section")
    section = Section.objects.create(name="Same Section")

    assert section.slug == "same-section-1"


@pytest.mark.django_db
def test_manufacturer_slug_is_generated_unique():
    Manufacturer.objects.create(name="First Brand")
    manufacturer = Manufacturer.objects.create(name="Second Brand", slug="first-brand")

    assert manufacturer.slug == "first-brand-1"


@pytest.mark.django_db
def test_collection_slug_is_generated_unique():
    manufacturer = Manufacturer.objects.create(name="Brand")

    Collection.objects.create(
        manufacturer=manufacturer,
        name="Same Collection",
    )
    collection = Collection.objects.create(
        manufacturer=manufacturer,
        name="Same Collection 2",
        slug="same-collection",
    )

    assert collection.slug == "same-collection-1"


@pytest.mark.django_db
def test_product_attribute_slug_is_generated_unique():
    ProductAttribute.objects.create(
        name="Same Attribute",
        type=ProductAttribute.AttributeType.TEXT,
    )
    attribute = ProductAttribute.objects.create(
        name="Same Attribute",
        type=ProductAttribute.AttributeType.TEXT,
    )

    assert attribute.slug == "same-attribute-1"


@pytest.mark.django_db
def test_product_attribute_option_slug_is_unique_inside_attribute():
    attribute = ProductAttribute.objects.create(
        name="Attribute",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    ProductAttributeOption.objects.create(attribute=attribute, value="Same Option")
    option = ProductAttributeOption.objects.create(
        attribute=attribute,
        value="Same Option 2",
        slug="same-option",
    )

    assert option.slug == "same-option-1"
