import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product


@pytest.mark.django_db
def test_filter_products_by_fuel_type():

    client = APIClient()

    Product.objects.create(
        name="Дровяная печь",
        price=10000,
        fuel_type="wood",
        is_active=True,
    )

    Product.objects.create(
        name="Газовая печь",
        price=10000,
        fuel_type="gas",
        is_active=True,
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "fuel_type": ["wood"]
    })

    assert response.status_code == 200

    results = response.json()["results"]

    names = [item["name"] for item in results]

    assert names == ["Дровяная печь"]
    assert "Газовая печь" not in names
@pytest.mark.django_db
def test_filter_products_by_heated_volume():

    client = APIClient()

    Product.objects.create(
        name="Печь 100",
        price=10000,
        heated_volume=100,
        is_active=True,
    )

    Product.objects.create(
        name="Печь 150",
        price=10000,
        heated_volume=150,
        is_active=True,
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "heated_volume": [100]
    })

    assert response.status_code == 200

    results = response.json()["results"]

    assert len(results) == 1
    assert results[0]["name"] == "Печь 100"
