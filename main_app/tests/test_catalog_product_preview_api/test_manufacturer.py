import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product, Manufacturer


@pytest.mark.django_db
def test_filter_products_by_manufacturer():

    client = APIClient()

    manufacturer1 = Manufacturer.objects.create(
        name="Brand1",
        slug="brand1"
    )

    manufacturer2 = Manufacturer.objects.create(
        name="Brand2",
        slug="brand2"
    )

    Product.objects.create(
        name="Печь 1",
        price=10000,
        manufacturer=manufacturer1,
        is_active=True
    )

    Product.objects.create(
        name="Печь 2",
        price=10000,
        manufacturer=manufacturer2,
        is_active=True
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "manufacturer": [manufacturer1.id]
    })

    results = response.json()["results"]

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["name"] == "Печь 1"