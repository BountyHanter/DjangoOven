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
        logo="manufacturers/test.jpg",
        slug="harvia",
    )
    # ---------------- SECTION LEVEL 1 ----------------
    parent_section = Section.objects.create(
        name="Основные печи",
        slug="main_oven",
        ordering=1,
    )

    # ---------------- SECTION LEVEL 2 ----------------
    child_section = Section.objects.create(
        name="Дровяные печи",
        slug="wood_oven",
        parent=parent_section,   # ← ВОТ ЭТО делает второй уровень
        ordering=1,
    )

    # ---------------- PRODUCT ----------------
    product = Product.objects.create(
        # --- base ---
        name="Тестовая печь MAX PRO",
        manufacturer=manufacturer,
        description="Полное описание товара",
        video_url="https://youtube.com/test",

        # --- prices ---
        price=150000,
        discount_price=120000,
        price_in_euro=True,

        # --- statuses ---
        free_delivery=True,
        in_stock=True,
        is_active=True,
        is_popular=True,
        is_new=True,
        is_bestseller=True,

        # --- params ---
        sku="SKU-123,SKU-456",
        series="Premium",
        dimensions="800x600x900",
        weight=85.5,
        steam_volume_from=10,
        steam_volume_to=20,
        stone_weight=90,

        # --- choices (ВАЖНО: строки-ключи) ---
        purpose="home",
        fuel_type="wood",
        heated_volume="100_150",
        power_kw="kw_14",
        firebox_material="steel",
        firebox_type="with_extension",
        installation_type="corner",
        combustion_type="long_burning",
        glass_count="two",
        fire_view="panoramic_glass",
        cladding_material="stone",
        heater_type="combined",
        water_circuit=True,
        stone_material="natural",
        steam_room_volume="20_30",
        firebox_orientation="horizontal",
        tank_type="samovar",
        door_mechanism="side_opening",
        chimney_diameter="115",

        # --- booleans ---
        heat_exchanger=True,
        glass_lift=True,
        damper=True,
        cooking_panel=True,

        # --- SEO ---
        seo_title="SEO заголовок",
        seo_description="SEO описание",
        seo_keywords="печь, баня, harvia",
    )
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
    url = reverse("catalog-product-detail", kwargs={"id": product.id})

    response = client.get(url)
    data = response.json()

    print("\n\n========== PRODUCT DETAIL ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("====================================\n\n")

    # --- smoke checks ---
    assert response.status_code == 200
    assert data["name"] == "Тестовая печь MAX PRO"
    assert len(data["images"]) == 2
    assert len(data["documents"]) == 2

    assert data["manufacturer"]["name"] == "Harvia"

    # sections: путь из 2 уровней
    assert len(data["sections"]) == 1
    assert [s["slug"] for s in data["sections"][0]] == ["main_oven", "wood_oven"]

    # choices + display
    assert data["fuel_type"] == "wood"
    assert "fuel_type_display" in data
    assert data["combustion_type"] == "long_burning"
    assert "combustion_type_display" in data
