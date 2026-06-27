from django.db.models import Case, F, IntegerField, Value, When, Count, Min, Max
from django.db.models.functions import Coalesce

from main_app.models import ProductAttributeValue
from main_app.models.product import Product

if __name__ == "__main__":
    import os

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django
    django.setup()


class CatalogService:

    @staticmethod
    def get_queryset(filters: list[dict] | None = None):
        """
        Главная точка входа для каталога:
        - применяем фильтры
        - применяем сортировку
        """

        qs = CatalogService.apply_filters(filters or [])
        qs = CatalogService.apply_sorting(qs)

        return qs

    @staticmethod
    def apply_filters(filters: list[dict]):
        """
        AND между фильтрами
        OR внутри одного фильтра (option_ids)
        """

        qs = Product.objects.all()

        for f in filters:
            f_type = f["type"]
            attribute_id = f.get("attribute_id")

            # -------------------------
            # CHOICE (OR внутри)
            # -------------------------
            if f_type == "choice":
                option_ids = f.get("option_ids") or []

                if option_ids:
                    qs = qs.filter(
                        attribute_values__attribute_id=attribute_id,
                        attribute_values__option_id__in=option_ids,
                    )

            # -------------------------
            # NUMBER
            # -------------------------
            elif f_type == "number":
                gte = f.get("gte")
                lte = f.get("lte")

                number_filter = {
                    "attribute_values__attribute_id": attribute_id,
                }

                if gte is not None:
                    number_filter["attribute_values__value_number__gte"] = gte

                if lte is not None:
                    number_filter["attribute_values__value_number__lte"] = lte

                qs = qs.filter(**number_filter)

            # -------------------------
            # BOOLEAN
            # -------------------------
            elif f_type == "bool":
                value = f.get("value")

                if value is not None:
                    qs = qs.filter(
                        attribute_values__attribute_id=attribute_id,
                        attribute_values__value_bool=value,
                    )

            # -------------------------
            # TEXT
            # -------------------------
            elif f_type == "text":
                value = f.get("value")

                if value:
                    qs = qs.filter(
                        attribute_values__attribute_id=attribute_id,
                        attribute_values__value_text__icontains=value,
                    )

            # -------------------------
            # MANUFACTURER
            # -------------------------

            elif f_type == "manufacturer":
                manufacturer_ids = f.get("ids") or []

                if manufacturer_ids:
                    qs = qs.filter(
                        manufacturer_id__in=manufacturer_ids,
                    )

            # -------------------------
            # PRICE
            # -------------------------

            elif f_type == "price":
                gte = f.get("gte")
                lte = f.get("lte")

                qs = qs.annotate(
                    actual_price=Coalesce(
                        "discount_price",
                        "price",
                        output_field=IntegerField(),
                    )
                )

                if gte is not None:
                    qs = qs.filter(actual_price__gte=gte)

                if lte is not None:
                    qs = qs.filter(actual_price__lte=lte)

            # -------------------------
            # DISCOUNT
            # -------------------------

            elif f_type == "has_discount":
                value = f.get("value")

                if value is True:
                    qs = qs.filter(
                        discount_price__isnull=False,
                    )

                elif value is False:
                    qs = qs.filter(
                        discount_price__isnull=True,
                    )

        return qs.distinct()

    @staticmethod
    def apply_sorting(qs):
        """
        Сортировка каталога:

        1. хит + приоритет
        2. хит без приоритета
        3. приоритет без хита
        4. остальное

        Внутри приоритетных групп:
        - priority ASC, потому что 1 — самый высокий приоритет

        Если товары одинаковые по группе/приоритету:
        - created_at DESC
        """

        qs = qs.annotate(
            sort_group=Case(

                # 1. хит + приоритет
                When(
                    is_bestseller=True,
                    priority__isnull=False,
                    then=Value(1),
                ),

                # 2. хит без приоритета
                When(
                    is_bestseller=True,
                    priority__isnull=True,
                    then=Value(2),
                ),

                # 3. приоритет без хита
                When(
                    is_bestseller=False,
                    priority__isnull=False,
                    then=Value(3),
                ),

                # 4. остальное
                default=Value(4),
                output_field=IntegerField(),
            )
        )

        return qs.order_by(
            "sort_group",
            F("priority").asc(nulls_last=True),
            "-created_at",
        )

    @staticmethod
    def get_available_filters(products_qs):
        """
        Динамическая выдача доступных фильтров.

        На вход получает queryset товаров после фильтрации.
        На выход отдаёт только те бренды, цены и характеристики,
        которые реально есть у текущих товаров.
        """

        products_qs = products_qs.annotate(
            actual_price=Coalesce(
                "discount_price",
                "price",
                output_field=IntegerField(),
            )
        )

        # -------------------------
        # PRICE
        # -------------------------

        price_data = products_qs.aggregate(
            min_price=Min("actual_price"),
            max_price=Max("actual_price"),
        )

        # -------------------------
        # DISCOUNT
        # -------------------------

        has_discount = products_qs.filter(
            discount_price__isnull=False,
        ).exists()

        # -------------------------
        # MANUFACTURERS
        # -------------------------

        manufacturers_qs = (
            products_qs
            .filter(
                manufacturer__isnull=False,
                manufacturer__is_active=True,
            )
            .values(
                "manufacturer_id",
                "manufacturer__name",
                "manufacturer__slug",
                "manufacturer__logo",
            )
            .annotate(
                products_count=Count("id", distinct=True),
            )
            .order_by("manufacturer__name")
        )

        manufacturers = [
            {
                "id": item["manufacturer_id"],
                "name": item["manufacturer__name"],
                "slug": item["manufacturer__slug"],
                "logo": item["manufacturer__logo"],
                "products_count": item["products_count"],
            }
            for item in manufacturers_qs
        ]

        # -------------------------
        # ATTRIBUTES
        # -------------------------

        attribute_values_qs = (
            ProductAttributeValue.objects
            .filter(
                product_id__in=products_qs.values("id"),
            )
            .select_related(
                "attribute",
                "option",
            )
            .order_by(
                "attribute__name",
            )
        )

        attributes_map = {}

        for attribute_value in attribute_values_qs:
            attribute = attribute_value.attribute

            attribute_data = attributes_map.setdefault(
                attribute.id,
                {
                    "id": attribute.id,
                    "name": attribute.name,
                    "slug": attribute.slug,
                    "type": attribute.type,
                    "unit": attribute.unit,
                    "allow_multiple": attribute.allow_multiple,
                    "_product_ids": set(),
                }
            )

            attribute_data["_product_ids"].add(attribute_value.product_id)

            # -------------------------
            # CHOICE
            # -------------------------

            if attribute.type == "choice":
                if not attribute_value.option:
                    continue

                if not attribute_value.option.is_active:
                    continue

                options = attribute_data.setdefault("options", {})

                option_data = options.setdefault(
                    attribute_value.option_id,
                    {
                        "id": attribute_value.option_id,
                        "value": attribute_value.option.value,
                        "slug": attribute_value.option.slug,
                        "_product_ids": set(),
                    }
                )

                option_data["_product_ids"].add(attribute_value.product_id)

            # -------------------------
            # NUMBER
            # -------------------------

            elif attribute.type == "number":
                if attribute_value.value_number is None:
                    continue

                numbers = attribute_data.setdefault("_numbers", [])
                numbers.append(attribute_value.value_number)

            # -------------------------
            # BOOLEAN
            # -------------------------

            elif attribute.type == "bool":
                if attribute_value.value_bool is None:
                    continue

                bool_values = attribute_data.setdefault("values", {})

                bool_data = bool_values.setdefault(
                    attribute_value.value_bool,
                    {
                        "value": attribute_value.value_bool,
                        "_product_ids": set(),
                    }
                )

                bool_data["_product_ids"].add(attribute_value.product_id)

            # -------------------------
            # TEXT
            # -------------------------

            elif attribute.type == "text":
                if not attribute_value.value_text:
                    continue

                text_values = attribute_data.setdefault("values", {})

                text_data = text_values.setdefault(
                    attribute_value.value_text,
                    {
                        "value": attribute_value.value_text,
                        "_product_ids": set(),
                    }
                )

                text_data["_product_ids"].add(attribute_value.product_id)

        attributes = []

        for attribute_data in attributes_map.values():
            attribute_type = attribute_data["type"]

            # -------------------------
            # CHOICE RESULT
            # -------------------------

            if attribute_type == "choice":
                options = []

                for option_data in attribute_data.get("options", {}).values():
                    option_data["products_count"] = len(
                        option_data.pop("_product_ids")
                    )
                    options.append(option_data)

                if not options:
                    continue

                options.sort(key=lambda item: item["value"])

                attribute_data["options"] = options

            # -------------------------
            # NUMBER RESULT
            # -------------------------

            elif attribute_type == "number":
                numbers = attribute_data.pop("_numbers", [])

                if not numbers:
                    continue

                attribute_data["min"] = min(numbers)
                attribute_data["max"] = max(numbers)
                attribute_data["products_count"] = len(
                    attribute_data["_product_ids"]
                )

            # -------------------------
            # BOOLEAN RESULT
            # -------------------------

            elif attribute_type == "bool":
                values = []

                for bool_data in attribute_data.get("values", {}).values():
                    bool_data["products_count"] = len(
                        bool_data.pop("_product_ids")
                    )
                    values.append(bool_data)

                if not values:
                    continue

                values.sort(key=lambda item: item["value"], reverse=True)

                attribute_data["values"] = values

            # -------------------------
            # TEXT RESULT
            # -------------------------

            elif attribute_type == "text":
                values = []

                for text_data in attribute_data.get("values", {}).values():
                    text_data["products_count"] = len(
                        text_data.pop("_product_ids")
                    )
                    values.append(text_data)

                if not values:
                    continue

                values.sort(key=lambda item: item["value"])

                attribute_data["values"] = values

            attribute_data["products_count"] = len(
                attribute_data.pop("_product_ids")
            )

            attributes.append(attribute_data)

        return {
            "price": {
                "min": price_data["min_price"],
                "max": price_data["max_price"],
            },
            "has_discount": has_discount,
            "manufacturers": manufacturers,
            "attributes": attributes,
        }

    @staticmethod
    def get_catalog_data(filters: list[dict] | None = None):
        """
        Полная выдача каталога:
        - товары
        - доступные фильтры для UI
        """

        filtered_qs = CatalogService.apply_filters(filters or [])

        products_qs = CatalogService.apply_sorting(filtered_qs)
        available_filters = CatalogService.get_available_filters(filtered_qs)

        return {
            "products": products_qs,
            "available_filters": available_filters,
        }

if __name__ == "__main__":
    def run_tests():
        print("\n--- ДРОВА + ДЛИТЕЛЬНОЕ ГОРЕНИЕ ---")
        print(
            CatalogService.apply_filters([
                {
                    "attribute_id": 1,
                    "type": "choice",
                    "option_id": 1
                },
                {
                    "attribute_id": 6,
                    "type": "bool",
                    "value": True
                }
            ])
        )

    run_tests()
