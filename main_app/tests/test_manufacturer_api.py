import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models import Manufacturer


@pytest.mark.django_db
def test_get_manufacturers_list_default_order():
    """
    Проверяем:
    - список брендов отдаётся
    - по умолчанию сортировка по имени (alphabetical)
    """

    client = APIClient()

    Manufacturer.objects.create(
        name="Zota",
        logo="manufacturers/z.jpg",
        is_active=True,
        slug="zota",
    )
    Manufacturer.objects.create(
        name="Harvia",
        logo="manufacturers/h.jpg",
        is_active=True,
        slug="harvia",
    )

    url = reverse("catalog-manufacturers")
    response = client.get(url)

    assert response.status_code == 200

    results = response.json()["results"]

    # alphabetical order
    assert results[0]["name"] == "Harvia"
    assert results[1]["name"] == "Zota"


@pytest.mark.django_db
def test_get_manufacturers_list_order_by_priority():
    """
    Проверяем сортировку по priority.
    """

    client = APIClient()

    Manufacturer.objects.create(
        name="Brand A",
        logo="manufacturers/a.jpg",
        priority=100,
        is_active=True,
        slug="brand-a",
    )

    Manufacturer.objects.create(
        name="Brand B",
        logo="manufacturers/b.jpg",
        priority=300,
        is_active=True,
        slug="brand-b",
    )

    Manufacturer.objects.create(
        name="Brand C",
        logo="manufacturers/c.jpg",
        priority=200,
        is_active=True,
        slug="brand-c",
    )

    url = reverse("catalog-manufacturers")
    response = client.get(f"{url}?ordering=priority")

    assert response.status_code == 200

    results = response.json()["results"]

    assert results[0]["name"] == "Brand B"
    assert results[1]["name"] == "Brand C"
    assert results[2]["name"] == "Brand A"


@pytest.mark.django_db
def test_get_manufacturers_same_priority_fallback_to_name():
    """
    Если priority одинаковый —
    проверяем fallback сортировку по имени.
    """

    client = APIClient()

    Manufacturer.objects.create(
        name="Zeta",
        logo="manufacturers/z.jpg",
        priority=100,
        is_active=True,
        slug="zeta",
    )

    Manufacturer.objects.create(
        name="Alpha",
        logo="manufacturers/a.jpg",
        priority=100,
        is_active=True,
        slug="alpha",
    )

    url = reverse("catalog-manufacturers")
    response = client.get(f"{url}?ordering=priority")

    assert response.status_code == 200

    results = response.json()["results"]

    assert results[0]["name"] == "Alpha"
    assert results[1]["name"] == "Zeta"


@pytest.mark.django_db
def test_get_manufacturer_detail():
    """
    Проверяем получение конкретного бренда по id.
    """

    client = APIClient()

    manufacturer = Manufacturer.objects.create(
        name="Harvia",
        slug="harvia",
        logo="manufacturers/h.jpg",
        description="Описание бренда",
        is_active=True,
    )

    url = reverse(
        "catalog-manufacturer-detail",
        kwargs={"id": manufacturer.id},
    )

    response = client.get(url)
    print(json.dumps(response.json(), indent=4, ensure_ascii=False))

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == manufacturer.id
    assert data["name"] == "Harvia"
    assert "description" in data


@pytest.mark.django_db
def test_inactive_manufacturer_not_available():
    """
    Неактивный бренд не должен быть доступен через detail API.
    """

    client = APIClient()

    manufacturer = Manufacturer.objects.create(
        name="Hidden Brand",
        slug="hidden",
        logo="manufacturers/h.jpg",
        is_active=False,
    )

    url = reverse(
        "catalog-manufacturer-detail",
        kwargs={"id": manufacturer.id},
    )

    response = client.get(url)

    assert response.status_code == 404