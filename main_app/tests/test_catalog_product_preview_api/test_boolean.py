import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product


@pytest.mark.django_db
def test_filter_products_by_boolean_field():

    client = APIClient()

    Product.objects.create(
        name="Печь с панелью",
        price=10000,
        cooking_panel=True,
        is_active=True,
    )

    Product.objects.create(
        name="Печь без панели",
        price=10000,
        is_active=True,
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "cooking_panel": True
    })

    assert response.status_code == 200

    results = response.json()["results"]

    assert len(results) == 1
    assert results[0]["name"] == "Печь с панелью"