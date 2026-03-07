import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product


@pytest.mark.django_db
def test_sort_products_by_price_asc():

    client = APIClient()

    Product.objects.create(name="Печь 300", price=300, is_active=True)
    Product.objects.create(name="Печь 100", price=100, is_active=True)
    Product.objects.create(name="Печь 200", price=200, is_active=True)

    url = reverse("catalog-products")

    response = client.get(url, {"ordering": "price_asc"})

    assert response.status_code == 200

    results = response.json()["results"]

    prices = [item["price"] for item in results]

    assert prices[:3] == [100, 200, 300]

@pytest.mark.django_db
def test_sort_products_by_price_desc():

    client = APIClient()

    Product.objects.create(name="Печь 300", price=300, is_active=True)
    Product.objects.create(name="Печь 100", price=100, is_active=True)
    Product.objects.create(name="Печь 200", price=200, is_active=True)

    url = reverse("catalog-products")

    response = client.get(url, {"ordering": "price_desc"})

    results = response.json()["results"]

    prices = [item["price"] for item in results]

    assert prices[:3] == [300, 200, 100]

@pytest.mark.django_db
def test_sort_products_by_new():

    client = APIClient()

    Product.objects.create(name="Старая печь", price=100, is_active=True)
    Product.objects.create(name="Новая печь", price=100, is_active=True)

    url = reverse("catalog-products")

    response = client.get(url, {"ordering": "new"})

    results = response.json()["results"]

    names = [item["name"] for item in results]

    assert names[0] == "Новая печь"