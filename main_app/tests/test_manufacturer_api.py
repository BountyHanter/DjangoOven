import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Manufacturer


@pytest.mark.django_db
def test_get_manufacturers_default_alphabetical_order():
    """
    По умолчанию бренды должны возвращаться
    в алфавитном порядке.
    """

    client = APIClient()

    Manufacturer.objects.create(name="Zota", logo="manufacturers/z.jpg")
    Manufacturer.objects.create(name="Harvia", logo="manufacturers/h.jpg")
    Manufacturer.objects.create(name="Aito", logo="manufacturers/a.jpg")

    url = reverse("catalog-manufacturers")
    response = client.get(url)

    assert response.status_code == 200

    results = response.json()["results"]

    names = [item["name"] for item in results]

    assert names == ["Aito", "Harvia", "Zota"]


@pytest.mark.django_db
def test_get_manufacturers_order_by_priority():
    """
    Проверяем сортировку по приоритету.
    Чем выше priority — тем выше бренд.
    """

    client = APIClient()

    Manufacturer.objects.create(
        name="Brand A",
        logo="manufacturers/a.jpg",
        priority=10,
    )

    Manufacturer.objects.create(
        name="Brand B",
        logo="manufacturers/b.jpg",
        priority=100,
    )

    Manufacturer.objects.create(
        name="Brand C",
        logo="manufacturers/c.jpg",
        priority=50,
    )

    url = reverse("catalog-manufacturers")
    response = client.get(url, {"ordering": "priority"})

    assert response.status_code == 200

    results = response.json()["results"]
    names = [item["name"] for item in results]

    assert names == ["Brand B", "Brand C", "Brand A"]


@pytest.mark.django_db
def test_priority_same_then_alphabetical():
    """
    Если приоритет одинаковый —
    сортировка должна идти по алфавиту.
    """

    client = APIClient()

    Manufacturer.objects.create(
        name="Zeta",
        logo="manufacturers/z.jpg",
        priority=50,
    )

    Manufacturer.objects.create(
        name="Alpha",
        logo="manufacturers/a.jpg",
        priority=50,
    )

    Manufacturer.objects.create(
        name="Beta",
        logo="manufacturers/b.jpg",
        priority=50,
    )

    url = reverse("catalog-manufacturers")
    response = client.get(url, {"ordering": "priority"})
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

    assert response.status_code == 200

    results = response.json()["results"]
    names = [item["name"] for item in results]

    assert names == ["Alpha", "Beta", "Zeta"]