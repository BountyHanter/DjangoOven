import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product


@pytest.mark.django_db
def test_filter_products_by_steam_volume_overlap():

    client = APIClient()

    Product.objects.create(
        name="Печь маленькая",
        price=10000,
        steam_volume_from=6,
        steam_volume_to=10,
        is_active=True,
    )

    Product.objects.create(
        name="Печь средняя",
        price=10000,
        steam_volume_from=10,
        steam_volume_to=20,
        is_active=True,
    )

    Product.objects.create(
        name="Печь большая",
        price=10000,
        steam_volume_from=25,
        steam_volume_to=40,
        is_active=True,
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "steam_volume_from": 8,
        "steam_volume_to": 15
    })

    assert response.status_code == 200

    results = response.json()["results"]

    names = [item["name"] for item in results]

    assert "Печь маленькая" in names
    assert "Печь средняя" in names
    assert "Печь большая" not in names