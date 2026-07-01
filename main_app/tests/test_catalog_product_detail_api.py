import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import (
    Product,
    ProductAttribute,
    ProductAttributeOption,
    ProductAttributeValue,
    ProductDocument,
    ProductImage,
    ProductVideo,
    Section,
)
from main_app.models.manufacturer import Manufacturer


def _attribute_by_slug(attributes, slug):
    return next(item for item in attributes if item["slug"] == slug)


def _section_path_slugs(paths):
    return {
        tuple(section["slug"] for section in path)
        for path in paths
    }


@pytest.fixture
def product_detail_data():
    manufacturer = Manufacturer.objects.create(
        name="Harvia Legend",
        slug="harvia-legend",
        logo="manufacturers/harvia-logo.png",
        seo_title="Harvia Legend официальный бренд",
        seo_description="Финские банные печи Harvia Legend",
        seo_keywords="harvia, legend, sauna",
        description="Большое описание производителя",
        video="https://video.example.com/brands/harvia",
        priority=500,
    )

    root_section = Section.objects.create(
        name="Каталог",
        slug="catalog-root",
        menu_name="Каталог",
        ordering=1,
        image="sections/catalog-root.jpg",
        description_main="Основной каталог",
        browser_title="Каталог печей",
        description="Полное описание корневого раздела",
        meta_description="Разделы каталога",
        meta_keywords="каталог, печи",
    )
    sauna_section = Section.objects.create(
        name="Банные печи",
        slug="sauna-stoves",
        parent=root_section,
        ordering=2,
        image="sections/sauna-stoves.jpg",
        description_main="Печи для бани",
        browser_title="Банные печи",
        description="Печи для разных парных",
        meta_description="Банные печи для каталога",
        meta_keywords="баня, печи",
    )
    wood_section = Section.objects.create(
        name="Дровяные печи",
        slug="wood-fired-stoves",
        parent=sauna_section,
        ordering=3,
        image="sections/wood-fired-stoves.jpg",
        description_main="Дровяные модели",
        browser_title="Дровяные печи",
        description="Дровяные печи для русской бани",
        meta_description="Дровяные печи",
        meta_keywords="дрова, печь",
    )
    accessories_section = Section.objects.create(
        name="Комплекты и аксессуары",
        slug="kits-and-accessories",
        parent=root_section,
        ordering=4,
        image="sections/accessories.jpg",
        description="Сопутствующие разделы",
    )

    product = Product.objects.create(
        name="Harvia Legend GreenFlame 240 Duo",
        manufacturer=manufacturer,
        description=(
            "Подробное описание товара с несколькими абзацами, "
            "особенностями топки, каменки и монтажа."
        ),
        schema="products/schema/legend-240-schema.pdf",
        price=189900,
        discount_price=174500,
        free_delivery=True,
        in_stock=True,
        is_active=True,
        is_new=True,
        is_bestseller=True,
        priority=7,
        sku="HL-240-DUO, HL-240-DUO-GF",
        series="Legend GreenFlame",
        seo_title="Harvia Legend GreenFlame 240 Duo купить",
        seo_description="Карточка товара Harvia Legend GreenFlame 240 Duo",
        seo_keywords="harvia legend, greenflame, банная печь",
    )
    product.sections.add(wood_section, accessories_section)

    ProductImage.objects.create(
        product=product,
        image="products/images/legend-main.webp",
        is_main=True,
        ordering=10,
    )
    ProductImage.objects.create(
        product=product,
        image="products/images/legend-side.webp",
        ordering=20,
    )
    ProductImage.objects.create(
        product=product,
        image="products/images/legend-firebox.webp",
        ordering=30,
    )

    ProductVideo.objects.create(
        product=product,
        url="https://video.example.com/products/legend-review.mp4",
        preview_url="https://cdn.example.com/previews/legend-review.webp",
        ordering=20,
    )
    ProductVideo.objects.create(
        product=product,
        url="https://www.youtube.com/watch?v=legend-installation",
        preview_url="https://img.youtube.com/vi/legend-installation/maxresdefault.jpg",
        ordering=10,
    )

    ProductDocument.objects.create(
        product=product,
        title="Инструкция по монтажу",
        file="products/documents/legend-installation.pdf",
        ordering=20,
    )
    ProductDocument.objects.create(
        product=product,
        title="Сертификат соответствия",
        file="products/documents/legend-certificate.pdf",
        ordering=10,
    )
    ProductDocument.objects.create(
        product=product,
        title="Гарантийный талон",
        file="products/documents/legend-warranty.pdf",
        ordering=30,
    )

    fuel_attribute = ProductAttribute.objects.create(
        name="Тип топлива",
        slug="fuel-type",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    wood_option = ProductAttributeOption.objects.create(
        attribute=fuel_attribute,
        value="Дрова",
        slug="wood",
    )
    ProductAttributeOption.objects.create(
        attribute=fuel_attribute,
        value="Газ",
        slug="gas",
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=fuel_attribute,
        option=wood_option,
    )

    materials_attribute = ProductAttribute.objects.create(
        name="Материалы отделки",
        slug="finish-materials",
        type=ProductAttribute.AttributeType.CHOICE,
        allow_multiple=True,
    )
    soapstone_option = ProductAttributeOption.objects.create(
        attribute=materials_attribute,
        value="Талькохлорит",
        slug="soapstone",
    )
    steel_option = ProductAttributeOption.objects.create(
        attribute=materials_attribute,
        value="Нержавеющая сталь",
        slug="stainless-steel",
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=materials_attribute,
        option=soapstone_option,
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=materials_attribute,
        option=steel_option,
    )

    power_attribute = ProductAttribute.objects.create(
        name="Мощность",
        slug="power-kw",
        type=ProductAttribute.AttributeType.NUMBER,
        unit="кВт",
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=power_attribute,
        value_number="18.50",
    )

    steam_volume_attribute = ProductAttribute.objects.create(
        name="Объем парной",
        slug="steam-volume",
        type=ProductAttribute.AttributeType.NUMBER,
        unit="м3",
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=steam_volume_attribute,
        value_number="24.00",
    )

    water_circuit_attribute = ProductAttribute.objects.create(
        name="Водяной контур",
        slug="water-circuit",
        type=ProductAttribute.AttributeType.BOOLEAN,
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=water_circuit_attribute,
        value_bool=True,
    )

    glass_lift_attribute = ProductAttribute.objects.create(
        name="Подъемное стекло",
        slug="glass-lift",
        type=ProductAttribute.AttributeType.BOOLEAN,
        hide_in_filter=True,
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=glass_lift_attribute,
        value_bool=False,
    )

    installation_note_attribute = ProductAttribute.objects.create(
        name="Комментарий к монтажу",
        slug="installation-note",
        type=ProductAttribute.AttributeType.TEXT,
    )
    ProductAttributeValue.objects.create(
        product=product,
        attribute=installation_note_attribute,
        value_text="Нужен негорючий экран и отступ от деревянной стены 500 мм.",
    )

    # Шумовые данные проверяют, что detail отдает только выбранный товар.
    other_product = Product.objects.create(
        name="Не тот товар",
        manufacturer=manufacturer,
        price=1,
        is_active=True,
    )
    other_product.sections.add(sauna_section)
    ProductImage.objects.create(
        product=other_product,
        image="products/images/other.webp",
        is_main=True,
    )

    return {
        "product": product,
        "manufacturer": manufacturer,
        "sections": [root_section, sauna_section, wood_section, accessories_section],
    }


@pytest.mark.django_db
def test_product_detail_api_returns_full_current_contract(product_detail_data):
    client = APIClient()
    product = product_detail_data["product"]

    url = reverse("catalog-product-detail", kwargs={"id": product.id})
    response = client.get(url)

    assert response.status_code == 200

    data = response.json()

    print("\n\n========== PRODUCT DETAIL ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("====================================\n\n")

    assert data["id"] == product.id
    assert data["name"] == "Harvia Legend GreenFlame 240 Duo"
    assert data["slug"] == "harvia-legend-greenflame-240-duo"
    assert data["manufacturer"] == {
        "id": product.manufacturer_id,
        "name": "Harvia Legend",
    }
    assert data["price"] == 189900
    assert data["discount_price"] == 174500
    assert data["description"].startswith("Подробное описание товара")
    assert data["schema"] == "/media/products/schema/legend-240-schema.pdf"
    assert data["free_delivery"] is True
    assert data["in_stock"] is True
    assert data["is_active"] is True
    assert data["is_new"] is True
    assert data["is_bestseller"] is True
    assert data["priority"] == 7
    assert data["sku"] == "HL-240-DUO, HL-240-DUO-GF"
    assert data["series"] == "Legend GreenFlame"
    assert data["seo_title"] == "Harvia Legend GreenFlame 240 Duo купить"
    assert data["seo_description"] == (
        "Карточка товара Harvia Legend GreenFlame 240 Duo"
    )
    assert data["seo_keywords"] == "harvia legend, greenflame, банная печь"
    assert "created_at" in data
    assert "updated_at" in data

    assert _section_path_slugs(data["sections"]) == {
        ("catalog-root", "sauna-stoves", "wood-fired-stoves"),
        ("catalog-root", "kits-and-accessories"),
    }

    assert [image["ordering"] for image in data["images"]] == [10, 20, 30]
    assert data["images"][0]["image"] == "/media/products/images/legend-main.webp"
    assert data["images"][0]["is_main"] is True
    assert "is_main" not in data["images"][1]
    assert data["images"][1]["image"] == "/media/products/images/legend-side.webp"
    assert data["images"][2]["image"] == "/media/products/images/legend-firebox.webp"

    assert [video["ordering"] for video in data["videos"]] == [10, 20]
    assert data["videos"][0]["url"] == (
        "https://www.youtube.com/watch?v=legend-installation"
    )
    assert data["videos"][0]["preview_url"] == (
        "https://img.youtube.com/vi/legend-installation/maxresdefault.jpg"
    )
    assert data["videos"][1]["url"] == (
        "https://video.example.com/products/legend-review.mp4"
    )

    assert [document["ordering"] for document in data["documents"]] == [10, 20, 30]
    assert [document["title"] for document in data["documents"]] == [
        "Сертификат соответствия",
        "Инструкция по монтажу",
        "Гарантийный талон",
    ]
    assert data["documents"][0]["file"] == (
        "/media/products/documents/legend-certificate.pdf"
    )

    attributes = data["attributes"]
    assert {attribute["slug"] for attribute in attributes} == {
        "finish-materials",
        "fuel-type",
        "glass-lift",
        "installation-note",
        "power-kw",
        "steam-volume",
        "water-circuit",
    }

    fuel_type = _attribute_by_slug(attributes, "fuel-type")
    assert fuel_type["name"] == "Тип топлива"
    assert fuel_type["type"] == ProductAttribute.AttributeType.CHOICE
    assert fuel_type["value"] == {
        "id": fuel_type["value"]["id"],
        "name": "Дрова",
        "slug": "wood",
    }

    finish_materials = _attribute_by_slug(attributes, "finish-materials")
    assert finish_materials["type"] == ProductAttribute.AttributeType.CHOICE
    assert finish_materials["value"] == [
        {
            "id": finish_materials["value"][0]["id"],
            "name": "Талькохлорит",
            "slug": "soapstone",
        },
        {
            "id": finish_materials["value"][1]["id"],
            "name": "Нержавеющая сталь",
            "slug": "stainless-steel",
        },
    ]

    power = _attribute_by_slug(attributes, "power-kw")
    assert power["type"] == ProductAttribute.AttributeType.NUMBER
    assert power["unit"] == "кВт"
    assert power["value"] == "18.50"

    steam_volume = _attribute_by_slug(attributes, "steam-volume")
    assert steam_volume["unit"] == "м3"
    assert steam_volume["value"] == "24.00"

    water_circuit = _attribute_by_slug(attributes, "water-circuit")
    assert water_circuit["type"] == ProductAttribute.AttributeType.BOOLEAN
    assert water_circuit["value"] is True

    glass_lift = _attribute_by_slug(attributes, "glass-lift")
    assert glass_lift["name"] == "Подъемное стекло"
    assert glass_lift["value"] is False

    installation_note = _attribute_by_slug(attributes, "installation-note")
    assert installation_note["type"] == ProductAttribute.AttributeType.TEXT
    assert installation_note["value"] == (
        "Нужен негорючий экран и отступ от деревянной стены 500 мм."
    )


@pytest.mark.django_db
def test_product_detail_api_returns_404_for_inactive_product(product_detail_data):
    client = APIClient()
    product = product_detail_data["product"]
    product.is_active = False
    product.save(update_fields=["is_active"])

    url = reverse("catalog-product-detail", kwargs={"id": product.id})
    response = client.get(url)

    assert response.status_code == 404
