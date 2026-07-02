import json
from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from main_app.models import Product
from main_app.tests.catalog_filter_data import create_catalog_filter_dataset


def _request_products(client, filters, ordering=None):
    params = {
        "filters": json.dumps(filters),
        "page_size": 100,
    }

    if ordering:
        params["ordering"] = ordering

    return client.get(reverse("catalog-products"), params)


def _section_path_slugs(paths):
    return {
        tuple(section["slug"] for section in path)
        for path in paths
    }


@pytest.mark.django_db
def test_catalog_products_api_filters_by_sections_attributes_and_price():
    client = APIClient()
    dataset = create_catalog_filter_dataset()

    filters = [
        {
            "type": "section",
            "ids": [dataset["sections"]["stoves"].id],
        },
        {
            "type": "manufacturer",
            "ids": [dataset["manufacturers"]["aurora"].id],
        },
        {
            "type": "choice",
            "attribute_id": dataset["attributes"]["fuel"].id,
            "option_ids": [
                dataset["options"]["wood_fuel"].id,
                dataset["options"]["gas_fuel"].id,
            ],
        },
        {
            "type": "choice",
            "attribute_id": dataset["attributes"]["finish"].id,
            "option_ids": [dataset["options"]["steel"].id],
        },
        {
            "type": "number",
            "attribute_id": dataset["attributes"]["power"].id,
            "gte": "14",
            "lte": "19",
        },
        {
            "type": "number",
            "attribute_id": dataset["attributes"]["steam_volume"].id,
            "gte": "16",
            "lte": "25",
        },
        {
            "type": "boolean",
            "attribute_id": dataset["attributes"]["water_circuit"].id,
            "value": True,
        },
        {
            "type": "price",
            "gte": 90000,
            "lte": 130000,
        },
    ]

    response = _request_products(client, filters)

    assert response.status_code == 200

    data = response.json()

    print("\n\n========== FILTERED PRODUCTS ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("=======================================\n\n")

    assert data["count"] == 2
    assert data["next"] is None
    assert data["previous"] is None

    results = data["results"]
    names = [item["name"] for item in results]

    assert names == [
        "Aurora Pro 18 Duo",
        "Aurora Compact 14",
    ]
    assert "BathLab Electro 10" not in names
    assert "BathLab Gas 22" not in names
    assert "Aurora Installation Kit" not in names
    assert "Aurora Hidden Prototype" not in names

    aurora_pro = results[0]
    assert aurora_pro["manufacturer"] == "Aurora"
    assert aurora_pro["price"] == 162000
    assert aurora_pro["discount_price"] == 129000
    assert aurora_pro["is_new"] is True
    assert aurora_pro["is_bestseller"] is True
    assert aurora_pro["priority"] == 1
    assert aurora_pro["has_video"] is True
    assert aurora_pro["power"] == {
        "name": "Мощность",
        "slug": "moshchnost",
        "value": "18.50",
        "unit": "кВт",
    }
    assert _section_path_slugs(aurora_pro["sections"]) == {
        ("catalog-root", "stoves", "wood-fired-stoves"),
        ("catalog-root", "accessories"),
    }
    assert [image["image"] for image in aurora_pro["images"]] == [
        "/media/products/images/aurora-pro-main.webp",
        "/media/products/images/aurora-pro-side.webp",
    ]
    assert aurora_pro["images"][0]["is_main"] is True
    assert "is_main" not in aurora_pro["images"][1]

    aurora_compact = results[1]
    assert aurora_compact["manufacturer"] == "Aurora"
    assert aurora_compact["price"] == 99000
    assert aurora_compact["discount_price"] is None
    assert aurora_compact["is_new"] is False
    assert aurora_compact["is_bestseller"] is False
    assert aurora_compact["priority"] == 3
    assert aurora_compact["has_video"] is False
    assert aurora_compact["power"] == {
        "name": "Мощность",
        "slug": "moshchnost",
        "value": "14.00",
        "unit": "кВт",
    }
    assert _section_path_slugs(aurora_compact["sections"]) == {
        ("catalog-root", "stoves", "wood-fired-stoves"),
    }
    assert aurora_compact["images"] == [
        {
            "id": aurora_compact["images"][0]["id"],
            "image": "/media/products/images/aurora-compact-main.webp",
            "ordering": 1,
            "is_main": True,
        }
    ]

    discount_response = _request_products(
        client,
        [
            *filters,
            {
                "type": "has_discount",
                "value": True,
            },
        ],
    )

    assert discount_response.status_code == 200

    discount_data = discount_response.json()
    assert discount_data["count"] == 1
    assert [
        item["name"]
        for item in discount_data["results"]
    ] == ["Aurora Pro 18 Duo"]


@pytest.mark.parametrize(
    "raw_filters",
    [
        "not-json",
        "{}",
        "[1]",
    ],
)
def test_catalog_products_api_returns_400_for_invalid_filters(raw_filters):
    client = APIClient()

    response = client.get(
        reverse("catalog-products"),
        {
            "filters": raw_filters,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Некорректный формат filters. "
            "Ожидается JSON-список объектов."
        )
    }


@pytest.mark.django_db
def test_catalog_products_api_orders_by_bestseller_priority_and_created_at():
    client = APIClient()
    now = timezone.now()

    regular_older = Product.objects.create(
        name="Regular older",
        price=10000,
        is_active=True,
    )
    Product.objects.filter(pk=regular_older.pk).update(
        created_at=now - timedelta(days=2),
    )

    regular_newer = Product.objects.create(
        name="Regular newer",
        price=10000,
        is_active=True,
    )
    Product.objects.filter(pk=regular_newer.pk).update(
        created_at=now - timedelta(days=1),
    )

    Product.objects.create(
        name="Priority only",
        price=10000,
        is_active=True,
        priority=5,
    )

    Product.objects.create(
        name="Bestseller no priority",
        price=10000,
        is_active=True,
        is_bestseller=True,
    )

    Product.objects.create(
        name="Bestseller priority 2",
        price=10000,
        is_active=True,
        is_bestseller=True,
        priority=2,
    )

    Product.objects.create(
        name="Bestseller priority 1",
        price=10000,
        is_active=True,
        is_bestseller=True,
        priority=1,
    )

    response = _request_products(client, [])

    assert response.status_code == 200

    names = [
        item["name"]
        for item in response.json()["results"]
    ]

    assert names == [
        "Bestseller priority 1",
        "Bestseller priority 2",
        "Bestseller no priority",
        "Priority only",
        "Regular newer",
        "Regular older",
    ]


@pytest.mark.django_db
def test_catalog_products_api_orders_by_requested_ordering():
    client = APIClient()
    now = timezone.now()

    expensive_old = Product.objects.create(
        name="Expensive old",
        price=200000,
        is_active=True,
    )
    Product.objects.filter(pk=expensive_old.pk).update(
        created_at=now - timedelta(days=3),
    )

    discounted_new = Product.objects.create(
        name="Discounted new",
        price=150000,
        discount_price=80000,
        is_active=True,
    )
    Product.objects.filter(pk=discounted_new.pk).update(
        created_at=now,
    )

    cheap_middle = Product.objects.create(
        name="Cheap middle",
        price=90000,
        is_active=True,
    )
    Product.objects.filter(pk=cheap_middle.pk).update(
        created_at=now - timedelta(days=1),
    )

    newest_response = _request_products(client, [], ordering="newest")
    price_asc_response = _request_products(client, [], ordering="price_asc")
    price_desc_response = _request_products(client, [], ordering="price_desc")

    assert newest_response.status_code == 200
    assert price_asc_response.status_code == 200
    assert price_desc_response.status_code == 200

    assert [
        item["name"]
        for item in newest_response.json()["results"]
    ] == [
        "Discounted new",
        "Cheap middle",
        "Expensive old",
    ]
    assert [
        item["name"]
        for item in price_asc_response.json()["results"]
    ] == [
        "Discounted new",
        "Cheap middle",
        "Expensive old",
    ]
    assert [
        item["name"]
        for item in price_desc_response.json()["results"]
    ] == [
        "Expensive old",
        "Cheap middle",
        "Discounted new",
    ]
