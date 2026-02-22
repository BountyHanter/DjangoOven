import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product, Section, Portfolio
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_get_portfolio_by_product():
    """
    Тест:
    - создаём 2 товара
    - каждому товару создаём по 2 портфолио
    - запрашиваем портфолио товара №2
    - должны получить ровно 2 записи
    """

    client = APIClient()

    manufacturer = Manufacturer.objects.create(name="Test")

    product1 = Product.objects.create(
        name="Товар 1",
        manufacturer=manufacturer,
        price=100,
    )

    product2 = Product.objects.create(
        name="Товар 2",
        manufacturer=manufacturer,
        price=100,
    )

    # портфолио товара 1
    Portfolio.objects.create(title="P1", picture="test.jpg", product=product1)
    Portfolio.objects.create(title="P2", picture="test.jpg", product=product1)

    # портфолио товара 2
    Portfolio.objects.create(title="P3", picture="test.jpg", product=product2)
    Portfolio.objects.create(title="P4", picture="test.jpg", product=product2)

    url = reverse("product-portfolio", kwargs={"product_id": product2.id})
    response = client.get(url)
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))

    assert response.status_code == 200
    assert response.json()["count"] == 2


@pytest.mark.django_db
def test_get_portfolio_by_section():
    """
    Тест:
    - создаём 2 категории
    - в каждой категории по 2 товара
    - каждому товару по 2 портфолио
    - запрашиваем портфолио категории №2
    - должны получить 4 портфолио (2 товара × 2 портфолио)
    """

    client = APIClient()

    manufacturer = Manufacturer.objects.create(name="Test")

    section1 = Section.objects.create(name="Категория 1", slug="cat-1")
    section2 = Section.objects.create(name="Категория 2", slug="cat-2")

    # товары категории 1
    p1 = Product.objects.create(name="T1", manufacturer=manufacturer, price=100)
    p2 = Product.objects.create(name="T2", manufacturer=manufacturer, price=100)

    # товары категории 2
    p3 = Product.objects.create(name="T3", manufacturer=manufacturer, price=100)
    p4 = Product.objects.create(name="T4", manufacturer=manufacturer, price=100)

    # привязка товаров к разделам
    p1.sections.add(section1)
    p2.sections.add(section1)

    p3.sections.add(section2)
    p4.sections.add(section2)

    # портфолио (по 2 на товар)
    for product in (p1, p2, p3, p4):
        Portfolio.objects.create(title=f"{product.name}-1", picture="test.jpg", product=product)
        Portfolio.objects.create(title=f"{product.name}-2", picture="test.jpg", product=product)

    url = reverse("catalog-portfolio")
    response = client.get(f"{url}?section={section2.id}")

    assert response.status_code == 200
    assert response.json()["count"] == 4