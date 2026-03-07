import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product


@pytest.mark.django_db
def test_filter_products_by_price_range():

    client = APIClient()

    Product.objects.create(
        name="Дешевая печь",
        price=30000,
        is_active=True,
    )

    Product.objects.create(
        name="Средняя печь",
        price=70000,
        is_active=True,
    )

    Product.objects.create(
        name="Дорогая печь",
        price=150000,
        is_active=True,
    )

    # товар со скидкой
    Product.objects.create(
        name="Скидочная печь",
        price=120000,
        discount_price=60000,
        is_active=True,
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "price_from": 50000,
        "price_to": 100000
    })

    assert response.status_code == 200

    results = response.json()["results"]

    names = [item["name"] for item in results]

    assert "Средняя печь" in names
    assert "Скидочная печь" in names

    assert "Дешевая печь" not in names
    assert "Дорогая печь" not in names

@pytest.mark.django_db
def test_filter_products_by_power_range():

    client = APIClient()

    Product.objects.create(
        name="Печь 10kw",
        price=10000,
        power_kw=10,
        is_active=True,
    )

    Product.objects.create(
        name="Печь 20kw",
        price=10000,
        power_kw=20,
        is_active=True,
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "power_kw_min": 15,
        "power_kw_max": 25
    })

    results = response.json()["results"]

    assert len(results) == 1
    assert results[0]["name"] == "Печь 20kw"