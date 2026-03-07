import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product, Section


@pytest.mark.django_db
def test_filter_products_by_section():

    client = APIClient()

    section1 = Section.objects.create(
        name="Раздел 1",
        slug="section1"
    )

    section2 = Section.objects.create(
        name="Раздел 2",
        slug="section2"
    )

    product1 = Product.objects.create(
        name="Печь 1",
        price=10000,
        is_active=True
    )

    product2 = Product.objects.create(
        name="Печь 2",
        price=20000,
        is_active=True
    )

    product1.sections.add(section1)
    product2.sections.add(section2)

    url = reverse("catalog-products")

    response = client.get(url, {
        "section": [section1.id]
    })

    data = response.json()
    results = data["results"]

    assert response.status_code == 200
    assert len(results) == 1
    assert results[0]["name"] == "Печь 1"