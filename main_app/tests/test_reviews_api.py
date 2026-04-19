import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Product, Review
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_get_reviews_by_product():
    """
    Тест:
    - создаём 3 товара
    - 1 отзыв у товара №1
    - 2 отзыва у товара №3
    - проверяем что API возвращает нужное количество отзывов
    """

    client = APIClient()

    # ---------- производитель ----------
    manufacturer = Manufacturer.objects.create(name="Тестовый бренд", slug="test")

    # ---------- товары ----------
    product1 = Product.objects.create(
        name="Товар 1",
        manufacturer=manufacturer,
        price=100,
    )

    Product.objects.create(
        name="Товар 2",
        manufacturer=manufacturer,
        price=100,
    )

    product3 = Product.objects.create(
        name="Товар 3",
        manufacturer=manufacturer,
        price=100,
    )

    # ---------- отзывы ----------
    Review.objects.create(
        name="Отзыв 1",
        client_name="Клиент 1",
        installation_time="1 день",
        location="Москва",
        work_description="Описание работ",
        date="2024-01-15",
        price=1000,
        video_url="video",
        product=product1,
    )
    Review.objects.create(
        name="Отзыв 2",
        client_name="Клиент 2",
        installation_time="1 день",
        location="Москва",
        date="2024-01-16",
        work_description="Описание работ",
        price=1000,
        video_url="video",
        product=product3,
    )

    Review.objects.create(
        name="Отзыв 3",
        client_name="Клиент 3",
        installation_time="1 день",
        location="Москва",
        date="2024-01-17",
        work_description="Описание работ",
        price=1000,
        video_url="video",
        product=product3,
    )

    # ---------- запрос отзывов товара 1 ----------
    url = reverse("product-reviews", kwargs={"product_id": product1.id})
    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["count"] == 1

    # ---------- запрос отзывов товара 3 ----------
    url = reverse("product-reviews", kwargs={"product_id": product3.id})
    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["count"] == 2


@pytest.mark.django_db
def test_get_all_reviews_ordered_newest_first():
    """
    Тест:
    Проверяем что отзывы возвращаются
    от новых к старым.
    """

    client = APIClient()

    manufacturer = Manufacturer.objects.create(name="Тестовый бренд", slug="test")

    product = Product.objects.create(
        name="Товар",
        manufacturer=manufacturer,
        price=100,
    )

    # старый отзыв
    old_review = Review.objects.create(
        name="Старый отзыв",
        client_name="Клиент 1",
        installation_time="1 день",
        location="Москва",
        work_description="Описание работ",
        price=1000,
        video_url="video",
        product=product,
    )

    # новый отзыв
    new_review = Review.objects.create(
        name="Новый отзыв",
        client_name="Клиент 2",
        installation_time="1 день",
        location="Москва",
        work_description="Описание работ",
        price=1000,
        video_url="video",
        product=product,
    )

    url = reverse("catalog-reviews")
    response = client.get(url)

    assert response.status_code == 200

    results = response.json()["results"]
    print(json.dumps(results, indent=2, ensure_ascii=False))

    # первый должен быть самый новый
    assert results[0]["id"] == new_review.id
    assert results[1]["id"] == old_review.id