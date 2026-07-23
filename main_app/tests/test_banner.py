import json
from datetime import timedelta

import pytest
from django.utils import timezone
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


@pytest.mark.django_db
def test_banner_api_orders_by_positive_priority_then_default_ordering():
    client = APIClient()
    now = timezone.now()

    no_priority_zero = Banner.objects.create(
        title="No priority zero",
        image="banners/no-priority-zero.jpg",
        priority=0,
    )
    no_priority_empty = Banner.objects.create(
        title="No priority empty",
        image="banners/no-priority-empty.jpg",
        priority=None,
    )
    priority_ten_old = Banner.objects.create(
        title="Priority ten old",
        image="banners/priority-ten-old.jpg",
        priority=10,
    )
    priority_ten_new = Banner.objects.create(
        title="Priority ten new",
        image="banners/priority-ten-new.jpg",
        priority=10,
    )
    priority_one = Banner.objects.create(
        title="Priority one",
        image="banners/priority-one.jpg",
        priority=1,
    )

    Banner.objects.filter(pk=no_priority_zero.pk).update(
        created_at=now - timedelta(days=4)
    )
    Banner.objects.filter(pk=no_priority_empty.pk).update(
        created_at=now - timedelta(days=1)
    )
    Banner.objects.filter(pk=priority_ten_old.pk).update(
        created_at=now - timedelta(days=3)
    )
    Banner.objects.filter(pk=priority_ten_new.pk).update(
        created_at=now - timedelta(days=2)
    )
    Banner.objects.filter(pk=priority_one.pk).update(
        created_at=now)

    response = client.get(reverse("banners"))

    assert response.status_code == 200
    assert [item["title"] for item in response.json()["results"]] == [
        "Priority one",
        "Priority ten new",
        "Priority ten old",
        "No priority empty",
        "No priority zero",
    ]
