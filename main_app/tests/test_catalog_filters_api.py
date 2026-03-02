import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models.section import Section
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_catalog_filters_api():

    client = APIClient()

    # --- sections ---
    parent = Section.objects.create(
        name="Основные печи",
        slug="main_oven",
        ordering=1,
    )

    Section.objects.create(
        name="Дочерняя печь",
        slug="child_oven",
        parent=parent,
        ordering=1,
    )

    # --- manufacturers ---
    Manufacturer.objects.create(
        name="Plamen",
        slug="plamen",
        is_active=True,
    )

    Manufacturer.objects.create(
        name="EasySteam",
        slug="easysteam",
        is_active=True,
    )

    url = reverse("catalog-filters")
    response = client.get(url)
    data = response.json()

    print(json.dumps(data, indent=4, ensure_ascii=False))

    assert response.status_code == 200

    # --- sections проверки ---
    assert "sections" in data
    assert len(data["sections"]) == 1
    assert data["sections"][0]["name"] == "Основные печи"

    assert len(data["sections"][0]["children"]) == 1
    assert data["sections"][0]["children"][0]["name"] == "Дочерняя печь"

    # --- manufacturers проверки ---
    assert "manufacturers" in data
    assert len(data["manufacturers"]) == 2

    manufacturer_names = [m["name"] for m in data["manufacturers"]]

    assert "Plamen" in manufacturer_names
    assert "EasySteam" in manufacturer_names

    # --- fuel type проверки ---
    assert "filters" in data
    assert "fuel_type" in data["filters"]

    assert len(data["filters"]["fuel_type"]) > 0

    values = [f["value"] for f in data["filters"]["fuel_type"]]
    assert "gas" in values
