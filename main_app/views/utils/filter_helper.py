import re

from django.db import models
from django.db.models import Min, Max, Count

from main_app.models.product import Product


FILTER_FIELDS = [
    "fuel_type",
    "heated_volume",

    "lining_material",
    "firebox_material",

    "firebox_type",
    "installation_type",

    "glass_count",
    "fire_view",

    "heater_type",
    "stone_material",
    "tank_type",

    "door_mechanism",

    "chimney_connection",
    "chimney_diameter",

    "water_circuit",
    "long_fire",
    "heat_exchanger",
    "glass_lift",
    "damper",
    "cooking_panel",
    "power_kw",
    "steam_volume",
]

RANGE_FILTERS = {
    "price": {
        "min_param": "price_from",
        "max_param": "price_to",
        "field": "final_price",
    },
    "power_kw": {
        "min_param": "power_kw_min",
        "max_param": "power_kw_max",
        "field": "power_kw",
    },
    "steam_volume": {
        "min_param": "steam_volume_from",
        "max_param": "steam_volume_to",
        "field": "steam_volume",
    },
}

SORTING_CONFIG = [
    {
        "value": "new",
        "label": "Сначала новые",
        "ordering": ["-created_at"],
    },
    {
        "value": "price_asc",
        "label": "Сначала дешёвые",
        "ordering": ["final_price", "-created_at"],
    },
    {
        "value": "price_desc",
        "label": "Сначала дорогие",
        "ordering": ["-final_price", "-created_at"],
    },
]

# Для фронта
SORTING_OPTIONS = [
    {
        "value": item["value"],
        "label": item["label"],
    }
    for item in SORTING_CONFIG
]

SORTING_MAP = {
    item["value"]: item["ordering"]
    for item in SORTING_CONFIG
}

DEFAULT_SORTING = "new"


def clean_label(label: str) -> str:
    """
    Убираем (кВт), (м³) и т.п. из названия фильтра
    """
    return re.sub(r"\s*\(.*?\)", "", label)


def build_choices(choices):
    return [
        {
            "value": value,
            "label": label,
        }
        for value, label in choices
    ]


def get_unique_values(field_name: str):
    """
    Для строковых полей без choices
    например chimney_diameter
    """
    values = (
        Product.objects
        .exclude(**{f"{field_name}__isnull": True})
        .exclude(**{field_name: ""})
        .values_list(field_name, flat=True)
        .distinct()
        .order_by(field_name)
    )

    return [
        {
            "value": v,
            "label": v,
        }
        for v in values
    ]


def get_price_filter():
    data = Product.objects.aggregate(
        min_price=Min("price"),
        max_price=Max("price"),
    )

    return {
        "field": "price",
        "label": "Цена",
        "type": "range",
        "min": data["min_price"],
        "max": data["max_price"],
    }


def get_counts(field_name: str):

    rows = (
        Product.objects
        .filter(is_active=True)
        .exclude(**{f"{field_name}__isnull": True})
        .values(field_name)
        .annotate(count=Count("id"))
    )

    return {
        row[field_name]: row["count"]
        for row in rows
    }

def generate_filters():

    filters = []

    for field in Product._meta.get_fields():

        field_name = field.name

        if field_name not in FILTER_FIELDS:
            continue

        label = clean_label(str(field.verbose_name))

        # получаем counts
        counts = get_counts(field_name)

        # ---------------- select (choices) ----------------
        if getattr(field, "choices", None):

            options = []

            for value, choice_label in field.choices:

                options.append({
                    "value": value,
                    "label": choice_label,
                    "count": counts.get(value, 0),
                })

            filters.append({
                "field": field_name,
                "label": label,
                "type": "select",
                "options": options,
            })

        # ---------------- boolean ----------------
        elif isinstance(field, models.BooleanField):

            true_count = Product.objects.filter(
                is_active=True,
                **{field_name: True}
            ).count()

            filters.append({
                "field": field_name,
                "label": label,
                "type": "boolean",
                "count": true_count,
            })

        # ---------------- range ----------------
        elif isinstance(field, (models.IntegerField, models.DecimalField)):

            config = RANGE_FILTERS.get(field_name)

            if config:
                filters.append({
                    "field": field_name,
                    "label": label,
                    "type": "range",
                    "params": {
                        "min": config["min_param"],
                        "max": config["max_param"],
                    },
                })

        # ---------------- CharField без choices ----------------
        elif isinstance(field, models.CharField):

            options = get_unique_values(field_name)

            for opt in options:
                opt["count"] = counts.get(opt["value"], 0)

            filters.append({
                "field": field_name,
                "label": label,
                "type": "select",
                "options": options,
            })

    # ---------------- price ----------------
    price_filter = get_price_filter()

    price_config = RANGE_FILTERS["price"]

    price_filter["params"] = {
        "min": price_config["min_param"],
        "max": price_config["max_param"],
    }

    filters.insert(0, price_filter)

    # ---------------- steam volume ----------------
    filters.append({
        "field": "steam_volume",
        "label": "Объём парной",
        "type": "range",
        "params": {
            "min": "steam_volume_from",
            "max": "steam_volume_to",
        }
    })

    return filters