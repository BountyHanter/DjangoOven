import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product, Section, Portfolio, PortfolioImage
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_get_portfolio_by_product():
    """
    Проверка фильтрации портфолио по товару.

    Сценарий:
    - создаётся производитель
    - создаются 2 товара
    - каждому товару создаётся по 2 портфолио
    - каждому портфолио добавляется изображение (PortfolioImage)
    - выполняется запрос портфолио для товара №2

    Ожидание:
    - API возвращает статус 200
    - возвращаются только портфолио выбранного товара
    - количество записей = 2
    """

    client = APIClient()

    manufacturer = Manufacturer.objects.create(name="Test", slug="test")

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
    p1 = Portfolio.objects.create(title="P1", product=product1)
    p2 = Portfolio.objects.create(title="P2", product=product1)

    # портфолио товара 2
    p3 = Portfolio.objects.create(title="P3", product=product2)
    p4 = Portfolio.objects.create(title="P4", product=product2)

    # изображения
    for portfolio in (p1, p2, p3, p4):
        PortfolioImage.objects.create(
            portfolio=portfolio,
            image="test.jpg",
            order=0,
        )

    url = reverse("product-portfolio", kwargs={"product_id": product2.id})
    response = client.get(url)

    print(json.dumps(response.json(), indent=4, ensure_ascii=False))

    assert response.status_code == 200
    assert response.json()["count"] == 2


@pytest.mark.django_db
def test_get_portfolio_by_section():
    """
    Проверка фильтрации портфолио по разделу каталога.

    Сценарий:
    - создаётся производитель
    - создаются 2 раздела каталога
    - в каждом разделе создаётся по 2 товара
    - каждому товару создаётся по 2 портфолио
    - каждому портфолио добавляется изображение
    - выполняется запрос портфолио по section_id второго раздела

    Ожидание:
    - API возвращает статус 200
    - возвращаются портфолио только товаров выбранного раздела
    - итоговое количество:
        2 товара × 2 портфолио = 4 записи
    """

    client = APIClient()

    manufacturer = Manufacturer.objects.create(name="Test", slug="test")

    section1 = Section.objects.create(name="Категория 1", slug="cat-1")
    section2 = Section.objects.create(name="Категория 2", slug="cat-2")

    # товары
    p1 = Product.objects.create(name="T1", manufacturer=manufacturer, price=100)
    p2 = Product.objects.create(name="T2", manufacturer=manufacturer, price=100)
    p3 = Product.objects.create(name="T3", manufacturer=manufacturer, price=100)
    p4 = Product.objects.create(name="T4", manufacturer=manufacturer, price=100)

    # привязка к разделам
    p1.sections.add(section1)
    p2.sections.add(section1)

    p3.sections.add(section2)
    p4.sections.add(section2)

    # портфолио + изображения
    for product in (p1, p2, p3, p4):
        pf1 = Portfolio.objects.create(title=f"{product.name}-1", product=product)
        pf2 = Portfolio.objects.create(title=f"{product.name}-2", product=product)

        PortfolioImage.objects.create(portfolio=pf1, image="test.jpg", order=0)
        PortfolioImage.objects.create(portfolio=pf2, image="test.jpg", order=0)

    url = reverse("catalog-portfolio")
    response = client.get(f"{url}?section={section2.id}")
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))


    assert response.status_code == 200
    assert response.json()["count"] == 4