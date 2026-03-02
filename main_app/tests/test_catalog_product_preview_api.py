import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product, ProductImage, Section
from main_app.models.manufacturer import Manufacturer


def get_results(response):
    return response.json()["results"]


@pytest.mark.django_db
def test_product_catalog_api():

    client = APIClient()

    manufacturer = Manufacturer.objects.create(
        name="Harvia",
        logo="manufacturers/test.jpg",
        slug="harvia",
    )
    parent_section = Section.objects.create(
        name="Основные печи",
        slug="main_oven",
        ordering=1,
    )

    child_section = Section.objects.create(
        name="Дровяные печи",
        slug="wood_oven",
        parent=parent_section,   # ← ВОТ ЭТО делает второй уровень
        ordering=1,
    )

    product = Product.objects.create(
        name="Тестовая печь",
        manufacturer=manufacturer,
        video_url="123",
        price=100000,
        discount_price=90000,
        fuel_type="wood",
        power_kw="kw_12",
        is_active=True,
    )

    ProductImage.objects.create(
        product=product,
        image="products/test.jpg",
        is_main=True,
        ordering=0,
    )

    ProductImage.objects.create(
        product=product,
        image="products/test1.jpg",
        is_main=False,
        ordering=1,
    )

    product.sections.add(child_section)

    url = reverse("catalog-products")
    response = client.get(url)

    data = response.json()
    results = get_results(response)

    print(json.dumps(data, indent=4, ensure_ascii=False))

    assert response.status_code == 200
    assert len(results) == 1

    item = results[0]

    assert item["name"] == "Тестовая печь"
    assert item["price"] == 100000
    assert item["discount_price"] == 90000

    assert item["fuel_type"] == "wood"
    assert item["fuel_type_display"] == "Дровяная"

    assert item["power_kw"] == "kw_12"

    assert len(item["images"]) == 2


@pytest.mark.django_db
def test_filter_products_by_multiple_sections(client):

    parent1 = Section.objects.create(name="Родитель1", slug="p1")
    child1 = Section.objects.create(name="Дочерний1", slug="c1", parent=parent1)

    parent2 = Section.objects.create(name="Родитель2", slug="p2")

    product1 = Product.objects.create(name="Печь1", price=10000, is_active=True)
    product2 = Product.objects.create(name="Печь2", price=20000, is_active=True)

    product1.sections.add(child1)
    product2.sections.add(parent2)

    url = reverse("catalog-products")

    response = client.get(url, {
        "section": [child1.id, parent2.id]
    })

    results = get_results(response)

    assert len(results) == 2


@pytest.mark.django_db
def test_filter_products_by_multiple_manufacturers(client):
    manufacturer1 = Manufacturer.objects.create(name="Brand1", logo="manufacturers/test1.jpg", slug="manufacturer1")
    manufacturer2 = Manufacturer.objects.create(name="Brand2", logo="manufacturers/test1.jpg", slug="manufacturer2")

    Product.objects.create(
        name="Печь1",
        price=10000,
        manufacturer=manufacturer1,
        is_active=True
    )

    Product.objects.create(
        name="Печь2",
        price=20000,
        manufacturer=manufacturer2,
        is_active=True
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "manufacturer": [manufacturer1.id, manufacturer2.id]
    })

    results = get_results(response)

    assert len(results) == 2


@pytest.mark.django_db
def test_filter_products_by_multiple_fuel_types(client):

    Product.objects.create(
        name="Печь дровяная",
        price=10000,
        fuel_type="wood",
        is_active=True
    )

    Product.objects.create(
        name="Печь газовая",
        price=20000,
        fuel_type="gas",
        is_active=True
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "fuel_type": ["wood", "gas"]
    })

    results = get_results(response)

    assert len(results) == 2


@pytest.mark.django_db
def test_filter_products_by_price_range(client):

    Product.objects.create(
        name="Дешёвая печь",
        price=30000,
        is_active=True
    )

    Product.objects.create(
        name="Средняя печь",
        price=70000,
        is_active=True
    )

    Product.objects.create(
        name="Дорогая печь",
        price=150000,
        is_active=True
    )

    Product.objects.create(
        name="Скидочная печь",
        price=120000,
        discount_price=60000,
        is_active=True
    )

    url = reverse("catalog-products")

    response = client.get(url, {
        "price_from": 50000,
        "price_to": 100000
    })

    results = get_results(response)

    names = [item["name"] for item in results]

    assert "Средняя печь" in names
    assert "Скидочная печь" in names

    assert "Дешёвая печь" not in names
    assert "Дорогая печь" not in names


# -------------------------------------------------------------------
# НОВЫЕ ТЕСТЫ: фильтры по choices / булевки / скидки / авто-сортировка
# -------------------------------------------------------------------

@pytest.mark.django_db
def test_filter_products_discount_only(client):
    Product.objects.create(
        name="Без скидки",
        price=100000,
        is_active=True,
    )
    Product.objects.create(
        name="Со скидкой",
        price=100000,
        discount_price=90000,
        is_active=True,
    )

    url = reverse("catalog-products")
    response = client.get(url, {"discount": "1"})

    assert response.status_code == 200
    results = get_results(response)

    assert len(results) == 1
    assert results[0]["name"] == "Со скидкой"


@pytest.mark.django_db
def test_filter_products_by_new_choice_fields(client):
    Product.objects.create(
        name="Печь A",
        price=50000,
        is_active=True,
        purpose="home",
        installation_type="wall",
        firebox_material="cast_iron",
        power_kw="kw_10",
        chimney_diameter="115",
    )
    Product.objects.create(
        name="Печь B",
        price=60000,
        is_active=True,
        purpose="cottage",
        installation_type="corner",
        firebox_material="steel",
        power_kw="kw_12",
        chimney_diameter="150",
    )

    url = reverse("catalog-products")
    response = client.get(url, {
        "purpose": ["home"],
        "installation_type": ["wall"],
        "firebox_material": ["cast_iron"],
        "power_kw": ["kw_10"],
        "chimney_diameter": ["115"],
    })

    assert response.status_code == 200
    results = get_results(response)

    assert len(results) == 1
    assert results[0]["name"] == "Печь A"


@pytest.mark.django_db
def test_filter_products_by_boolean_field(client):
    Product.objects.create(
        name="С варочной панелью",
        price=70000,
        is_active=True,
        cooking_panel=True,
    )
    Product.objects.create(
        name="Без панели",
        price=70000,
        is_active=True,
        cooking_panel=False,
    )

    url = reverse("catalog-products")
    response = client.get(url, {"cooking_panel": "1"})

    assert response.status_code == 200
    results = get_results(response)

    assert len(results) == 1
    assert results[0]["name"] == "С варочной панелью"


@pytest.mark.django_db
def test_unknown_filter_param_is_ignored(client):
    Product.objects.create(name="Печь X", price=10000, is_active=True)
    Product.objects.create(name="Печь Y", price=20000, is_active=True)

    url = reverse("catalog-products")
    response = client.get(url, {"какойто_мусор": "123"})

    # важно: не 400/500, а нормально игнорируем
    assert response.status_code == 200
    results = get_results(response)
    assert len(results) == 2


@pytest.mark.django_db
def test_auto_ordering_by_model_field_price(client):
    Product.objects.create(name="Печь 300", price=300, is_active=True)
    Product.objects.create(name="Печь 100", price=100, is_active=True)
    Product.objects.create(name="Печь 200", price=200, is_active=True)

    url = reverse("catalog-products")

    # auto sort: ordering=price
    response = client.get(url, {"ordering": "price"})
    assert response.status_code == 200
    results = get_results(response)
    names = [x["name"] for x in results]
    assert names[:3] == ["Печь 100", "Печь 200", "Печь 300"]

    # auto sort: ordering=-price
    response = client.get(url, {"ordering": "-price"})
    assert response.status_code == 200
    results = get_results(response)
    names = [x["name"] for x in results]
    assert names[:3] == ["Печь 300", "Печь 200", "Печь 100"]