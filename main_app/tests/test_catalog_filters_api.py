import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from main_app.tests.catalog_filter_data import create_catalog_filter_dataset


def _section_by_slug(sections, slug):
    for section in sections:
        if section["slug"] == slug:
            return section

        found = _section_by_slug(section["children"], slug)

        if found:
            return found

    return None


def _attribute_by_slug(attributes, slug):
    return next(item for item in attributes if item["slug"] == slug)


def _option_counts(attribute):
    return {
        option["slug"]: option["products_count"]
        for option in attribute["options"]
    }


def _bool_counts(attribute):
    return {
        item["value"]: item["products_count"]
        for item in attribute["values"]
    }


@pytest.mark.django_db
def test_catalog_filters_api_returns_dynamic_filters_and_counts():
    client = APIClient()
    dataset = create_catalog_filter_dataset()

    response = client.get(reverse("catalog-filters"))

    assert response.status_code == 200

    data = response.json()

    print("\n\n========== CATALOG FILTERS ==========")
    print(json.dumps(data, indent=4, ensure_ascii=False))
    print("=====================================\n\n")

    assert data["price"] == {
        "min": 45000,
        "max": 210000,
    }
    assert data["has_discount"] is True

    manufacturers = {
        manufacturer["slug"]: manufacturer
        for manufacturer in data["manufacturers"]
    }
    assert list(manufacturers) == [
        "aurora",
        "bathlab",
    ]
    assert manufacturers["aurora"]["name"] == "Aurora"
    assert manufacturers["aurora"]["logo"] == "manufacturers/aurora.webp"
    assert manufacturers["aurora"]["products_count"] == 3
    assert manufacturers["bathlab"]["products_count"] == 2

    root = _section_by_slug(data["sections"], "catalog-root")
    stoves = _section_by_slug(data["sections"], "stoves")
    wood = _section_by_slug(data["sections"], "wood-fired-stoves")
    electric = _section_by_slug(data["sections"], "electric-stoves")
    gas = _section_by_slug(data["sections"], "gas-stoves")
    accessories = _section_by_slug(data["sections"], "accessories")

    assert root["products_count"] == 5
    assert root["count"] == 5
    assert root["description_main"] == "Главный раздел каталога"
    assert root["image"] == "/media/sections/catalog-root.webp"
    assert root["browser_title"] == "Каталог печей"
    assert root["description"] == "Полное описание каталога"
    assert root["meta_description"] == "SEO описание каталога"
    assert root["meta_keywords"] == "каталог, печи"
    assert root["ordering"] == 1
    assert stoves["products_count"] == 4
    assert stoves["count"] == 4
    assert stoves["description_main"] == "Раздел с печами"
    assert stoves["image"] == "/media/sections/stoves.webp"
    assert stoves["browser_title"] == "Печи"
    assert stoves["description"] == "Полное описание раздела печей"
    assert stoves["meta_description"] == "SEO описание печей"
    assert stoves["meta_keywords"] == "печи"
    assert stoves["ordering"] == 1
    assert wood["products_count"] == 2
    assert electric["products_count"] == 1
    assert gas["products_count"] == 1
    assert accessories["products_count"] == 2

    attributes = data["attributes"]
    assert [attribute["slug"] for attribute in attributes] == [
        "finish-material",
        "fuel-type",
        "moshchnost",
        "water-circuit",
        "steam-volume",
        "glass-lift",
    ]
    assert {attribute["slug"] for attribute in attributes} == {
        "finish-material",
        "fuel-type",
        "glass-lift",
        "moshchnost",
        "steam-volume",
        "water-circuit",
    }

    fuel = _attribute_by_slug(attributes, "fuel-type")
    assert fuel["type"] == "choice"
    assert fuel["allow_multiple"] is False
    assert fuel["products_count"] == 4
    assert [option["slug"] for option in fuel["options"]] == [
        "gas",
        "wood",
        "electric",
    ]
    assert _option_counts(fuel) == {
        "electric": 1,
        "gas": 1,
        "wood": 2,
    }

    finish = _attribute_by_slug(attributes, "finish-material")
    assert finish["type"] == "choice"
    assert finish["allow_multiple"] is True
    assert finish["products_count"] == 4
    assert [option["slug"] for option in finish["options"]] == [
        "soapstone",
        "steel",
        "ceramic",
        "cast-iron",
    ]
    assert _option_counts(finish) == {
        "cast-iron": 1,
        "ceramic": 1,
        "soapstone": 1,
        "steel": 2,
    }

    power = _attribute_by_slug(attributes, "moshchnost")
    assert power["type"] == "number"
    assert power["unit"] == "кВт"
    assert power["products_count"] == 4
    assert power["min"] == 10.0
    assert power["max"] == 22.0

    steam_volume = _attribute_by_slug(attributes, "steam-volume")
    assert steam_volume["unit"] == "м3"
    assert steam_volume["products_count"] == 4
    assert steam_volume["min"] == 12.0
    assert steam_volume["max"] == 30.0

    water_circuit = _attribute_by_slug(attributes, "water-circuit")
    assert water_circuit["type"] == "boolean"
    assert _bool_counts(water_circuit) == {
        True: 2,
    }

    glass_lift = _attribute_by_slug(attributes, "glass-lift")
    assert _bool_counts(glass_lift) == {
        True: 2,
    }

    filtered_response = client.get(
        reverse("catalog-filters"),
        {
            "filters": json.dumps(
                [
                    {
                        "type": "section",
                        "ids": [dataset["sections"]["stoves"].id],
                    },
                    {
                        "type": "manufacturer",
                        "ids": [dataset["manufacturers"]["aurora"].id],
                    },
                    {
                        "type": "boolean",
                        "attribute_id": dataset["attributes"]["water_circuit"].id,
                        "value": True,
                    },
                ]
            )
        },
    )

    assert filtered_response.status_code == 200

    filtered_data = filtered_response.json()

    assert filtered_data["price"] == {
        "min": 99000,
        "max": 129000,
    }
    assert [
        manufacturer["slug"]
        for manufacturer in filtered_data["manufacturers"]
    ] == ["aurora"]
    assert filtered_data["manufacturers"][0]["products_count"] == 2

    filtered_root = _section_by_slug(filtered_data["sections"], "catalog-root")
    filtered_stoves = _section_by_slug(filtered_data["sections"], "stoves")
    filtered_wood = _section_by_slug(
        filtered_data["sections"],
        "wood-fired-stoves",
    )
    filtered_electric = _section_by_slug(
        filtered_data["sections"],
        "electric-stoves",
    )
    filtered_gas = _section_by_slug(filtered_data["sections"], "gas-stoves")
    filtered_accessories = _section_by_slug(
        filtered_data["sections"],
        "accessories",
    )

    assert filtered_root["products_count"] == 2
    assert filtered_root["count"] == 2
    assert filtered_stoves["products_count"] == 2
    assert filtered_stoves["count"] == 2
    assert filtered_wood["products_count"] == 2
    assert filtered_wood["count"] == 2
    assert filtered_electric["products_count"] == 0
    assert filtered_electric["count"] == 0
    assert filtered_gas["products_count"] == 0
    assert filtered_gas["count"] == 0
    assert filtered_accessories["products_count"] == 1
    assert filtered_accessories["count"] == 1

    filtered_attributes = filtered_data["attributes"]

    filtered_fuel = _attribute_by_slug(filtered_attributes, "fuel-type")
    assert filtered_fuel["products_count"] == 2
    assert _option_counts(filtered_fuel) == {
        "wood": 2,
    }

    filtered_finish = _attribute_by_slug(filtered_attributes, "finish-material")
    assert filtered_finish["products_count"] == 2
    assert _option_counts(filtered_finish) == {
        "soapstone": 1,
        "steel": 2,
    }

    filtered_power = _attribute_by_slug(filtered_attributes, "moshchnost")
    assert filtered_power["products_count"] == 2
    assert filtered_power["min"] == 14.0
    assert filtered_power["max"] == 18.5

    filtered_water_circuit = _attribute_by_slug(
        filtered_attributes,
        "water-circuit",
    )
    assert _bool_counts(filtered_water_circuit) == {
        True: 2,
    }


@pytest.mark.parametrize(
    "raw_filters",
    [
        "not-json",
        "{}",
        "[1]",
    ],
)
def test_catalog_filters_api_returns_400_for_invalid_filters(raw_filters):
    client = APIClient()

    response = client.get(
        reverse("catalog-filters"),
        {
            "filters": raw_filters,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": (
            "Некорректный формат filters. "
            "Ожидается JSON-список объектов."
        )
    }
