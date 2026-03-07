import json
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import (
    Product,
    ProductImage,
    ProductDocument,
    Section,
)
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_product_detail_api_full():

    client = APIClient()

    # ---------------- MANUFACTURER ----------------
    manufacturer = Manufacturer.objects.create(
        name="Harvia",
        slug="harvia",
        logo="manufacturers/test.jpg",
    )

    # ---------------- SECTIONS ----------------

    parent_section = Section.objects.create(
        name="Основные печи",
        slug="main_oven",
        ordering=1,
    )

    child_section = Section.objects.create(
        name="Дровяные печи",
        slug="wood_oven",
        parent=parent_section,
        ordering=1,
    )

    # ---------------- PRODUCT ----------------

    product = Product.objects.create(

        # --- основное ---
        name="Тестовая печь MAX PRO",
        manufacturer=manufacturer,
        description="Полное описание товара",
        video_url="https://youtube.com/test",

        # --- цены ---
        price=150000,
        discount_price=120000,

        # --- статусы ---
        free_delivery=True,
        in_stock=True,
        is_active=True,
        is_new=True,
        is_bestseller=True,

        # --- параметры ---
        sku="SKU-123,SKU-456",
        series="Premium",

        dimensions="800x600x900",
        weight=85,

        steam_volume_from=10,
        steam_volume_to=20,

        stone_weight=90,

        # --- choices ---
        fuel_type="wood",
        heated_volume="100",

        firebox_material="steel",
        firebox_type="with_extension",

        installation_type="corner",

        glass_count="two",
        fire_view="straight_glass",

        heater_type="combined",
        water_circuit=True,

        stone_material="natural",

        tank_type="samovar",

        door_mechanism="side_opening",

        chimney_diameter="115",
        chimney_connection="top",

        power_kw=14,

        # --- boolean параметры ---
        heat_exchanger=True,
        glass_lift=True,
        damper=True,
        cooking_panel=True,

        # --- SEO ---
        seo_title="SEO заголовок",
        seo_description="SEO описание",
        seo_keywords="печь, баня, harvia",
    )

    # связь с разделом
    product.sections.add(child_section)

    # ---------------- IMAGES ----------------

    ProductImage.objects.create(
        product=product,
        image="products/test_main.jpg",
        is_main=True,
        ordering=0,
    )

    ProductImage.objects.create(
        product=product,
        image="products/test_2.jpg",
        is_main=False,
        ordering=1,
    )

    # ---------------- DOCUMENTS ----------------

    ProductDocument.objects.create(
        product=product,
        title="Инструкция",
        file="docs/manual.pdf",
        ordering=0,
    )

    ProductDocument.objects.create(
        product=product,
        title="Сертификат",
        file="docs/cert.pdf",
        ordering=1,
    )

    # ---------------- REQUEST ----------------

    url = reverse(
        "catalog-product-detail",
        kwargs={"id": product.id},
    )

    response = client.get(url)

    assert response.status_code == 200

    data = response.json()

    print("\n\n========== PRODUCT DETAIL ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("====================================\n\n")

    # ---------------- BASIC CHECKS ----------------

    assert data["name"] == "Тестовая печь MAX PRO"

    assert data["price"] == 150000
    assert data["discount_price"] == 120000

    # ---------------- MANUFACTURER ----------------

    assert data["manufacturer"]["name"] == "Harvia"

    # ---------------- IMAGES ----------------

    assert len(data["images"]) == 2

    # главное изображение
    assert any(img["is_main"] for img in data["images"])

    # ---------------- DOCUMENTS ----------------

    assert len(data["documents"]) == 2

    titles = [doc["title"] for doc in data["documents"]]

    assert "Инструкция" in titles
    assert "Сертификат" in titles

    # ---------------- SECTIONS PATH ----------------

    assert len(data["sections"]) == 1

    path = data["sections"][0]

    assert [s["slug"] for s in path] == [
        "main_oven",
        "wood_oven",
    ]

    # ---------------- CHOICES ----------------

    assert data["fuel_type"] == "wood"
    assert "fuel_type_display" in data

    # ---------------- BOOLEAN ----------------

    assert data["water_circuit"] is True
    assert data["heat_exchanger"] is True
    assert data["glass_lift"] is True
    assert data["damper"] is True
    assert data["cooking_panel"] is True

    # ---------------- NUMERIC ----------------

    assert data["power_kw"] == 14

    # ---------------- STEAM VOLUME ----------------

    assert data["steam_volume_from"] == 10
    assert data["steam_volume_to"] == 20