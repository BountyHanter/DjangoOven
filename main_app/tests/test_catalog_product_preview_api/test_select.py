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

    assert len(results) == 1
    assert results[0]["fuel_type"] == "wood"