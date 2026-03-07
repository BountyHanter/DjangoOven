import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.models.banner import Banner
from main_app.models.section import Section
from main_app.models.manufacturer import Manufacturer


@pytest.mark.django_db
def test_banner_filter_by_section():

    client = APIClient()

    manufacturer = Manufacturer.objects.create(
        name="Harvia",
        slug="harvia",
    )

    section1 = Section.objects.create(
        name="Дровяные",
        slug="wood",
        ordering=1,
    )

    section2 = Section.objects.create(
        name="Газовые",
        slug="gas",
        ordering=2,
    )

    # баннер для section1
    banner1 = Banner.objects.create(
        title="Banner 1",
        image="banners/1.jpg",
        manufacturer=manufacturer,
    )
    banner1.sections.add(section1)

    # баннер для section2
    banner2 = Banner.objects.create(
        title="Banner 2",
        image="banners/2.jpg",
    )
    banner2.sections.add(section2)

    # глобальный баннер
    banner3 = Banner.objects.create(
        title="Banner global",
        image="banners/3.jpg",
    )

    url = reverse("banners")

    response = client.get(url, {"section": section1.id})

    assert response.status_code == 200

    data = response.json()
    results = data["results"]

    print(json.dumps(results, indent=4, ensure_ascii=False))

    assert len(results) == 2

    titles = {item["title"] for item in results}

    assert "Banner 1" in titles
    assert "Banner global" in titles
    assert "Banner 2" not in titles