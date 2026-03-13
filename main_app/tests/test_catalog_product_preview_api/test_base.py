import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product, ProductImage, Section
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_catalog_returns_products():

    client = APIClient()

    manufacturer = Manufacturer.objects.create(
        name="Harvia",
        slug="harvia",
    )

    parent = Section.objects.create(
        name="Основные печи",
        slug="main",
        ordering=1,
    )

    child = Section.objects.create(
        name="Дровяные печи",
        slug="wood",
        parent=parent,
        ordering=1,
    )

    product = Product.objects.create(
        name="Тестовая печь",
        manufacturer=manufacturer,
        price=100000,
        discount_price=90000,
        fuel_type="wood",
        power_kw=12,
        video_url="test",
        is_active=True,
    )

    product.sections.add(child)

    ProductImage.objects.create(
        product=product,
        image="products/test.jpg",
        is_main=True,
        ordering=0,
    )

    url = reverse("catalog-products")
    response = client.get(url)

    assert response.status_code == 200

    data = response.json()
    results = data["results"]
    print(json.dumps(results, indent=4, ensure_ascii=False))

    assert len(results) == 1

    item = results[0]

    assert item["name"] == "Тестовая печь"
    assert item["price"] == 100000
    assert item["discount_price"] == 90000
    assert item["power_kw"] == 12

    assert len(item["images"]) == 1