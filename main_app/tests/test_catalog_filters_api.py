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

    Manufacturer.objects.create(
        name="Печи Мальника",
        slug="malnik",
        is_active=True,
    )
    Manufacturer.objects.create(
        name="3Thermo",
        slug="3thermo",
        is_active=True,
    )
    Manufacturer.objects.create(
        name="Zota",
        slug="zota",
        is_active=True,
    )
    Manufacturer.objects.create(
        name="Везувий",
        slug="vezuviy",
        is_active=True,
    )

    response = client.get(reverse("catalog-filters"))
    assert response.status_code == 200

    names = [m["name"] for m in response.json()["manufacturers"]]
    assert names == [
        "Печи Мальника",
        "3Thermo",
        "Zota",
        "Везувий",
    ]
