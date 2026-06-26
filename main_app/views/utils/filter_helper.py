import re

from django.db import models
from django.db.models import (
    Case,
    Count,
    DecimalField,
    Exists,
    F,
    IntegerField,
    Max,
    Min,
    OuterRef,
    Q,
    Value,
    When,
)

from main_app.models.product import Product, ProductVideo
from main_app.models.section import Section


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
    "oven",
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
        "value": "popular",
        "label": "Сначала популярные",
        "ordering": ["-is_bestseller", "-created_at"],
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


def annotate_catalog_queryset(queryset):
    return queryset.annotate(
        final_price=Case(
            When(discount_price__isnull=False, then=F("discount_price")),
            default=F("price"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        has_video=Exists(
            ProductVideo.objects.filter(product_id=OuterRef("pk"))
        ),
    )


def get_catalog_queryset(with_related=False):
    queryset = Product.objects.filter(is_active=True)

    if with_related:
        queryset = queryset.select_related("manufacturer").prefetch_related(
            "images",
            "sections",
        )

    return annotate_catalog_queryset(queryset)


def is_filter_excluded(exclude_filter, filter_name):
    if exclude_filter is None:
        return False

    if isinstance(exclude_filter, (list, tuple, set)):
        return filter_name in exclude_filter

    return exclude_filter == filter_name


def apply_product_filters(queryset, filters, exclude_filter=None):
    discount = filters.get("discount")

    if discount and not is_filter_excluded(exclude_filter, "discount"):
        queryset = queryset.filter(discount_price__isnull=False)

    search_query = filters.get("search")

    if search_query:
        queryset = queryset.filter(Q(name__icontains=search_query))

    section_ids = filters.get("section")

    if section_ids and not is_filter_excluded(exclude_filter, "section"):
        sections = Section.objects.filter(
            id__in=section_ids,
            is_active=True,
        )

        all_section_ids = []

        for section in sections:
            all_section_ids.extend(section.get_descendants_ids())

        queryset = queryset.filter(sections__id__in=all_section_ids).distinct()

    manufacturer_ids = filters.get("manufacturer")

    if manufacturer_ids and not is_filter_excluded(exclude_filter, "manufacturer"):
        queryset = queryset.filter(
            manufacturer__id__in=manufacturer_ids,
            manufacturer__is_active=True,
        )

    for field in FILTER_FIELDS:
        if is_filter_excluded(exclude_filter, field):
            continue

        value = filters.get(field)

        if value is None:
            continue

        if isinstance(value, list):
            queryset = queryset.filter(**{f"{field}__in": value})
        else:
            queryset = queryset.filter(**{field: value})

    price_from = filters.get("price_from")
    price_to = filters.get("price_to")

    if price_from and not is_filter_excluded(exclude_filter, "price"):
        queryset = queryset.filter(final_price__gte=price_from)

    if price_to and not is_filter_excluded(exclude_filter, "price"):
        queryset = queryset.filter(final_price__lte=price_to)

    power_kw_min = filters.get("power_kw_min")
    power_kw_max = filters.get("power_kw_max")

    if power_kw_min and not is_filter_excluded(exclude_filter, "power_kw"):
        queryset = queryset.filter(power_kw__gte=power_kw_min)

    if power_kw_max and not is_filter_excluded(exclude_filter, "power_kw"):
        queryset = queryset.filter(power_kw__lte=power_kw_max)

    steam_from = filters.get("steam_volume_from")
    steam_to = filters.get("steam_volume_to")

    if steam_from is not None and not is_filter_excluded(exclude_filter, "steam_volume"):
        queryset = queryset.filter(steam_volume_to__gte=steam_from)

    if steam_to is not None and not is_filter_excluded(exclude_filter, "steam_volume"):
        queryset = queryset.filter(steam_volume_from__lte=steam_to)

    return queryset


def apply_product_ordering(queryset, filters):
    ordering = filters.get("ordering", DEFAULT_SORTING)

    if ordering == "popular":
        queryset = queryset.annotate(
            bestseller_priority_group=Case(
                When(
                    is_bestseller=True,
                    priority__isnull=False,
                    then=Value(0),
                ),
                When(is_bestseller=True, then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            ),
            bestseller_priority_value=Case(
                When(
                    is_bestseller=True,
                    priority__isnull=False,
                    then=F("priority"),
                ),
                default=Value(None),
                output_field=IntegerField(),
            ),
        )

        return queryset.order_by(
            "bestseller_priority_group",
            "bestseller_priority_value",
            "-created_at",
        )

    ordering_fields = SORTING_MAP.get(
        ordering,
        SORTING_MAP[DEFAULT_SORTING],
    )

    return queryset.order_by(*ordering_fields)


def get_filtered_product_queryset(
    filters,
    with_related=False,
    with_ordering=False,
    exclude_filter=None,
):
    queryset = get_catalog_queryset(with_related=with_related)
    queryset = apply_product_filters(
        queryset,
        filters,
        exclude_filter=exclude_filter,
    )

    if with_ordering:
        queryset = apply_product_ordering(queryset, filters)

    return queryset


def get_unique_values(queryset, field_name: str):
    """
    Для полей без choices, где нужны уникальные значения из БД
    (например chimney_diameter и heated_volume)
    """
    queryset = queryset.exclude(**{f"{field_name}__isnull": True})

    field = Product._meta.get_field(field_name)

    if isinstance(field, models.CharField):
        queryset = queryset.exclude(**{field_name: ""})

    values = (
        queryset
        .values_list(field_name, flat=True)
        .distinct()
        .order_by(field_name)
    )

    return [
        {
            "value": v,
            "label": str(v),
        }
        for v in values
    ]


def get_range_filter(
    queryset,
    field_name: str,
    label: str,
    min_param: str,
    max_param: str,
):
    data = queryset.aggregate(
        min_value=Min(field_name),
        max_value=Max(field_name),
    )

    if data["min_value"] is None or data["max_value"] is None:
        return None

    return {
        "field": field_name,
        "label": label,
        "type": "range",
        "min": data["min_value"],
        "max": data["max_value"],
        "params": {
            "min": min_param,
            "max": max_param,
        },
    }


def get_steam_volume_filter(queryset):
    data = queryset.aggregate(
        min_value=Min("steam_volume_from"),
        max_value=Max("steam_volume_to"),
    )

    if data["min_value"] is None or data["max_value"] is None:
        return None

    return {
        "field": "steam_volume",
        "label": "Объём парной",
        "type": "range",
        "min": data["min_value"],
        "max": data["max_value"],
        "params": {
            "min": "steam_volume_from",
            "max": "steam_volume_to",
        },
    }


def get_counts(queryset, field_name: str):
    rows = (
        queryset
        .exclude(**{f"{field_name}__isnull": True})
        .values(field_name)
        .annotate(count=Count("id", distinct=True))
    )

    return {
        row[field_name]: row["count"]
        for row in rows
    }


def append_filter_if_not_empty(filters, filter_data):
    if filter_data is not None:
        filters.append(filter_data)


def generate_filters(queryset=None, selected_filters=None):
    if queryset is None:
        queryset = get_catalog_queryset()

    def get_facet_queryset(filter_name):
        if selected_filters is None:
            return queryset

        return get_filtered_product_queryset(
            selected_filters,
            exclude_filter=filter_name,
        )

    filter_items = []

    price_queryset = get_facet_queryset("price")
    price_filter = get_range_filter(
        price_queryset,
        "final_price",
        "Цена",
        RANGE_FILTERS["price"]["min_param"],
        RANGE_FILTERS["price"]["max_param"],
    )

    if price_filter:
        price_filter["field"] = "price"
        filter_items.append(price_filter)

    for field in Product._meta.get_fields():

        field_name = field.name

        if field_name not in FILTER_FIELDS:
            continue

        label = clean_label(str(field.verbose_name))

        facet_queryset = get_facet_queryset(field_name)
        counts = get_counts(facet_queryset, field_name)

        # ---------------- select (choices) ----------------
        if getattr(field, "choices", None):

            options = []

            for value, choice_label in field.choices:
                count = counts.get(value, 0)

                if count <= 0:
                    continue

                options.append({
                    "value": value,
                    "label": choice_label,
                    "count": count,
                })

            if options:
                filter_items.append({
                    "field": field_name,
                    "label": label,
                    "type": "select",
                    "options": options,
                })

        # ---------------- boolean ----------------
        elif isinstance(field, models.BooleanField):

            true_count = facet_queryset.filter(
                **{field_name: True}
            ).count()

            if true_count > 0:
                filter_items.append({
                    "field": field_name,
                    "label": label,
                    "type": "boolean",
                    "count": true_count,
                })

        # ---------------- select (unique values for integer) ----------------
        elif field_name == "heated_volume":

            options = get_unique_values(facet_queryset, field_name)

            for opt in options:
                opt["count"] = counts.get(opt["value"], 0)

            options = [
                opt
                for opt in options
                if opt["count"] > 0
            ]

            if options:
                filter_items.append({
                    "field": field_name,
                    "label": label,
                    "type": "select",
                    "options": options,
                })

        # ---------------- range ----------------
        elif isinstance(field, (models.IntegerField, models.DecimalField)):

            config = RANGE_FILTERS.get(field_name)

            if config:
                append_filter_if_not_empty(
                    filter_items,
                    get_range_filter(
                        facet_queryset,
                        field_name,
                        label,
                        config["min_param"],
                        config["max_param"],
                    ),
                )

        # ---------------- CharField без choices ----------------
        elif isinstance(field, models.CharField):

            options = get_unique_values(facet_queryset, field_name)

            for opt in options:
                opt["count"] = counts.get(opt["value"], 0)

            options = [
                opt
                for opt in options
                if opt["count"] > 0
            ]

            if options:
                filter_items.append({
                    "field": field_name,
                    "label": label,
                    "type": "select",
                    "options": options,
                })

    # ---------------- discount ----------------
    discount_queryset = get_facet_queryset("discount")
    discount_count = discount_queryset.filter(
        discount_price__isnull=False,
    ).count()

    if discount_count > 0:
        filter_items.append({
            "field": "discount",
            "label": "Со скидкой",
            "type": "boolean",
            "count": discount_count,
        })

    # ---------------- steam volume ----------------
    append_filter_if_not_empty(
        filter_items,
        get_steam_volume_filter(get_facet_queryset("steam_volume")),
    )

    return filter_items
