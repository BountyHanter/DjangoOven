import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product

@pytest.mark.django_db
def test_unknown_filter_param_is_ignored():

    client = APIClient()

    Product.objects.create(
        name="Печь A",
        price=10000,
        is_active=True,
    )

    Product.objects.create(
        name="Печь B",
        price=20000,
        is_active=True,
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "какойто_мусор": "123"
    })

    assert response.status_code == 200

    results = response.json()["results"]

    # товары не должны отфильтроваться
    assert len(results) == 2