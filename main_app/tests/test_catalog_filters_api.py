import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product
from main_app.models.section import Section
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_catalog_filters_api():

    client = APIClient()

    # ---------------- SECTIONS ----------------

    parent = Section.objects.create(
        name="Основные печи",
        slug="main_oven",
        ordering=1,
    )

    Section.objects.create(
        name="Дровяные печи",
        slug="wood_oven",
        parent=parent,
        ordering=1,
    )

    # ---------------- MANUFACTURERS ----------------

    plamen = Manufacturer.objects.create(
        name="Plamen",
        slug="plamen",
        is_active=True,
    )

    easysteam = Manufacturer.objects.create(
        name="EasySteam",
        slug="easysteam",
        is_active=True,
    )

    # ---------------- PRODUCTS ----------------

    product_a = Product.objects.create(
        name="Печь A",
        price=10000,
        power_kw=10,
        heated_volume=100,
        chimney_diameter="115",
        manufacturer=plamen,
        is_active=True,
    )

    product_b = Product.objects.create(
        name="Печь B",
        price=20000,
        discount_price=18000,
        oven=True,
        power_kw=20,
        heated_volume=150,
        chimney_diameter="120",
        manufacturer=easysteam,
        is_active=True,
    )

    product_c = Product.objects.create(
        name="Печь C",
        price=30000,
        power_kw=30,
        heated_volume=100,
        chimney_diameter="115",
        manufacturer=plamen,
        is_active=True,
    )

    child_section = Section.objects.get(slug="wood_oven")

    product_a.sections.add(parent)
    product_b.sections.add(child_section)
    product_c.sections.add(child_section)

    # ---------------- REQUEST ----------------

    url = reverse("catalog-filters")

    response = client.get(url)

    assert response.status_code == 200

    data = response.json()

    print("\n\n========== FILTERS ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("=============================\n\n")

    # ---------------- SECTIONS ----------------

    assert "sections" in data
    assert len(data["sections"]) == 1

    parent_section = data["sections"][0]

    assert parent_section["name"] == "Основные печи"

    assert len(parent_section["children"]) == 1
    assert parent_section["children"][0]["name"] == "Дровяные печи"

    # ---------------- MANUFACTURERS ----------------

    assert "manufacturers" in data
    assert len(data["manufacturers"]) == 2

    manufacturer_names = [m["name"] for m in data["manufacturers"]]

    assert "Plamen" in manufacturer_names
    assert "EasySteam" in manufacturer_names

    # ---------------- FILTERS ----------------

    assert "filters" in data

    filters = data["filters"]

    assert isinstance(filters, list)
    assert len(filters) > 0

    # проверяем структуру фильтра
    first_filter = filters[0]

    assert "field" in first_filter
    assert "label" in first_filter
    assert "type" in first_filter

    # ---------------- PRICE RANGE ----------------

    price_filter = next(
        f for f in filters if f["field"] == "price"
    )

    assert price_filter["type"] == "range"

    assert price_filter["min"] == 10000
    assert price_filter["max"] == 30000

    assert price_filter["params"]["min"] == "price_from"
    assert price_filter["params"]["max"] == "price_to"

    # ---------------- CHIMNEY DIAMETER ----------------

    chimney_filter = next(
        f for f in filters if f["field"] == "chimney_diameter"
    )

    assert chimney_filter["type"] == "select"

    options = chimney_filter["options"]

    values = [o["value"] for o in options]

    assert "115" in values
    assert "120" in values

    # должны быть только уникальные значения
    assert len(values) == 2

    # ---------------- POWER RANGE ----------------

    power_filter = next(
        f for f in filters if f["field"] == "power_kw"
    )

    assert power_filter["type"] == "range"

    assert power_filter["params"]["min"] == "power_kw_min"
    assert power_filter["params"]["max"] == "power_kw_max"

    # ---------------- HEATED VOLUME ----------------

    heated_filter = next(
        f for f in filters if f["field"] == "heated_volume"
    )

    assert heated_filter["type"] == "select"

    heated_options = heated_filter["options"]

    heated_values = [o["value"] for o in heated_options]

    assert heated_values == [100, 150]

    heated_counts = {
        o["value"]: o["count"]
        for o in heated_options
    }

    assert heated_counts[100] == 2
    assert heated_counts[150] == 1

    # ---------------- DISCOUNT ----------------

    discount_filter = next(
        f for f in filters if f["field"] == "discount"
    )

    assert discount_filter["type"] == "boolean"
    assert discount_filter["count"] == 1

    # ---------------- OVEN ----------------

    oven_filter = next(
        f for f in filters if f["field"] == "oven"
    )

    assert oven_filter["type"] == "boolean"
    assert oven_filter["count"] == 1

    # ---------------- SORTING ----------------

    assert "sorting" in data

    sorting = data["sorting"]

    assert isinstance(sorting, list)
    assert len(sorting) > 0

    sorting_values = [s["value"] for s in sorting]

    assert "new" in sorting_values
    assert "popular" in sorting_values
    assert "price_asc" in sorting_values
    assert "price_desc" in sorting_values


@pytest.mark.django_db
def test_catalog_filters_manufacturers_default_order():
    client = APIClient()

    malnik = Manufacturer.objects.create(
        name="Печи Мальника",
        slug="malnik",
        is_active=True,
    )
    thermo = Manufacturer.objects.create(
        name="3Thermo",
        slug="3thermo",
        is_active=True,
    )
    zota = Manufacturer.objects.create(
        name="Zota",
        slug="zota",
        is_active=True,
    )
    vezuviy = Manufacturer.objects.create(
        name="Везувий",
        slug="vezuviy",
        is_active=True,
    )

    for manufacturer in [malnik, thermo, zota, vezuviy]:
        Product.objects.create(
            name=f"Печь {manufacturer.name}",
            price=10000,
            manufacturer=manufacturer,
            is_active=True,
        )

    response = client.get(reverse("catalog-filters"))
    assert response.status_code == 200

    names = [m["name"] for m in response.json()["manufacturers"]]
    assert names == [
        "3Thermo",
        "Zota",
        "Везувий",
        "Печи Мальника",
    ]


@pytest.mark.django_db
def test_catalog_filters_are_limited_by_selected_filters():
    client = APIClient()

    sauna = Section.objects.create(
        name="Печи для бани",
        slug="sauna",
        ordering=1,
    )
    fireplace = Section.objects.create(
        name="Камины",
        slug="fireplace",
        ordering=2,
    )

    brand_a = Manufacturer.objects.create(
        name="Brand A",
        slug="brand-a",
        is_active=True,
    )
    brand_b = Manufacturer.objects.create(
        name="Brand B",
        slug="brand-b",
        is_active=True,
    )

    matching = Product.objects.create(
        name="Дровяная печь с духовкой",
        price=10000,
        fuel_type="wood",
        heated_volume=100,
        chimney_diameter="115",
        oven=True,
        manufacturer=brand_a,
        is_active=True,
    )
    matching.sections.add(sauna)

    wrong_fuel = Product.objects.create(
        name="Газовая печь с духовкой",
        price=20000,
        fuel_type="gas",
        heated_volume=150,
        chimney_diameter="120",
        oven=True,
        manufacturer=brand_a,
        is_active=True,
    )
    wrong_fuel.sections.add(sauna)

    wrong_section = Product.objects.create(
        name="Дровяной камин с духовкой",
        price=30000,
        fuel_type="wood",
        heated_volume=200,
        chimney_diameter="130",
        oven=True,
        manufacturer=brand_b,
        is_active=True,
    )
    wrong_section.sections.add(fireplace)

    response = client.get(reverse("catalog-filters"), {
        "section": [sauna.id],
        "fuel_type": ["wood"],
        "oven": True,
    })

    assert response.status_code == 200

    data = response.json()
    filters = data["filters"]

    fuel_filter = next(f for f in filters if f["field"] == "fuel_type")
    assert [option["value"] for option in fuel_filter["options"]] == ["wood"]
    assert fuel_filter["options"][0]["count"] == 1

    heated_filter = next(f for f in filters if f["field"] == "heated_volume")
    assert [option["value"] for option in heated_filter["options"]] == [100]

    chimney_filter = next(f for f in filters if f["field"] == "chimney_diameter")
    assert [option["value"] for option in chimney_filter["options"]] == ["115"]

    assert [section["id"] for section in data["sections"]] == [sauna.id]
    manufacturer_names = [
        manufacturer["name"]
        for manufacturer in data["manufacturers"]
    ]
    assert manufacturer_names == ["Brand A"]
