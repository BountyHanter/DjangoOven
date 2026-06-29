from collections import defaultdict
from decimal import Decimal, InvalidOperation

from django.db.models import (
    Case,
    Count,
    Exists,
    F,
    IntegerField,
    Max,
    Min,
    OuterRef,
    Prefetch,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from config.utils.pagination import DefaultPagination
from main_app.models.attribute import ProductAttributeValue
from main_app.models.product import Product, ProductImage, ProductVideo
from main_app.models.section import Section


class CatalogService:
    BOOLEAN_TYPES = {"bool", "boolean"}
    POWER_ATTRIBUTE_SLUG = "moshchnost"

    @staticmethod
    def _normalize_id(value):
        if value in (None, "") or isinstance(value, bool):
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_id_list(value):
        if value in (None, ""):
            return []

        if isinstance(value, (list, tuple, set)):
            raw_values = value
        else:
            raw_values = [value]

        ids = []

        for raw_value in raw_values:
            parts = (
                raw_value.split(",")
                if isinstance(raw_value, str)
                else [raw_value]
            )

            for part in parts:
                if isinstance(part, str):
                    part = part.strip()

                if part in (None, "") or isinstance(part, bool):
                    continue

                try:
                    ids.append(int(part))
                except (TypeError, ValueError):
                    continue

        return ids

    @staticmethod
    def _normalize_number(value):
        if value in (None, "") or isinstance(value, bool):
            return None

        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_bool(value):
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in {"true", "1", "yes", "y"}:
                return True

            if normalized in {"false", "0", "no", "n"}:
                return False

        return None

    @staticmethod
    def _filter_by_attribute_exists(qs, attribute_id, **conditions):
        attribute_values = ProductAttributeValue.objects.filter(
            product_id=OuterRef("pk"),
            attribute_id=attribute_id,
            **conditions,
        )

        return qs.filter(Exists(attribute_values))

    @staticmethod
    def _get_section_ids_with_descendants(section_ids):
        """
        Возвращает выбранные разделы + всех их потомков.

        Работает с любой глубиной вложенности.
        """

        normalized_ids = set()

        for section_id in section_ids:
            try:
                normalized_ids.add(int(section_id))
            except (TypeError, ValueError):
                continue

        if not normalized_ids:
            return []

        rows = Section.objects.filter(
            is_active=True,
        ).values(
            "id",
            "parent_id",
        )

        children_by_parent = defaultdict(list)
        active_section_ids = set()

        for row in rows:
            section_id = row["id"]
            parent_id = row["parent_id"]

            active_section_ids.add(section_id)

            if parent_id:
                children_by_parent[parent_id].append(section_id)

        result_ids = set()
        stack = [
            section_id
            for section_id in normalized_ids
            if section_id in active_section_ids
        ]

        while stack:
            section_id = stack.pop()

            if section_id in result_ids:
                continue

            result_ids.add(section_id)
            stack.extend(children_by_parent.get(section_id, []))

        return list(result_ids)

    @staticmethod
    def get_products_queryset(filters: list[dict] | None = None):
        """
        Базовая выдача товаров каталога:
        - только активные товары
        - применяем фильтры
        - применяем сортировку

        Пагинацию здесь НЕ делаем.
        """

        qs = CatalogService.apply_filters(filters or [])
        qs = CatalogService.apply_sorting(qs)

        return qs

    @staticmethod
    def get_products_page(request, filters: list[dict] | None = None):
        """
        Базовая выдача товаров с пагинацией.
        """

        qs = CatalogService.get_products_queryset(filters)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(qs, request)

        return {
            "paginator": paginator,
            "page": page,
            "queryset": qs,
        }

    @staticmethod
    def get_preview_products_queryset(filters: list[dict] | None = None):
        """
        Queryset для preview-карточек товаров.

        Используется для:
        GET /api/v1/catalog/products/

        Здесь:
        - применяем фильтры
        - подготавливаем данные для карточки
        - применяем сортировку
        """

        qs = CatalogService.apply_filters(filters or [])
        qs = CatalogService.prepare_preview_queryset(qs)
        qs = CatalogService.apply_sorting(qs)

        return qs

    @staticmethod
    def get_preview_products_page(request, filters: list[dict] | None = None):
        """
        Preview-выдача товаров с пагинацией.
        """

        qs = CatalogService.get_preview_products_queryset(filters)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(qs, request)

        return {
            "paginator": paginator,
            "page": page,
            "queryset": qs,
        }

    @staticmethod
    def prepare_preview_queryset(qs):
        """
        Подготовка queryset для preview-карточек товара.

        Добавляем:
        - manufacturer
        - images
        - sections
        - has_video
        - power_value / power_name / power_unit из EAV по slug "moshchnost"
        """

        power_values = ProductAttributeValue.objects.filter(
            product_id=OuterRef("pk"),
            attribute__slug=CatalogService.POWER_ATTRIBUTE_SLUG,
            value_number__isnull=False,
        ).order_by("id")

        has_video_qs = ProductVideo.objects.filter(
            product_id=OuterRef("pk"),
        )

        preview_images_qs = ProductImage.objects.order_by(
            "-is_main",
            "ordering",
            "id",
        )

        return (
            qs
            .select_related("manufacturer")
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=preview_images_qs,
                    to_attr="preview_images",
                ),
                "sections",
            )
            .annotate(
                has_video=Exists(has_video_qs),
                power_value=Subquery(
                    power_values.values("value_number")[:1],
                ),
                power_name=Subquery(
                    power_values.values("attribute__name")[:1],
                ),
                power_unit=Subquery(
                    power_values.values("attribute__unit")[:1],
                ),
            )
        )

    @staticmethod
    def get_filters_data(filters: list[dict] | None = None):
        """
        Отдельная выдача доступных фильтров.

        Важно:
        - применяем те же самые фильтры
        - НЕ применяем сортировку
        - НЕ применяем пагинацию
        - считаем фильтры по полной отфильтрованной выборке
        """

        qs = CatalogService.apply_filters(filters or [])

        return CatalogService.get_available_filters(qs)

    @staticmethod
    def apply_filters(filters: list[dict]):
        """
        AND между фильтрами.
        OR внутри одного фильтра, например option_ids.
        """

        qs = Product.objects.filter(is_active=True)

        for f in filters:
            f_type = f.get("type")
            raw_attribute_id = f.get("attribute_id")
            attribute_id = CatalogService._normalize_id(raw_attribute_id)

            if not f_type:
                continue

            # -------------------------
            # SECTION
            # -------------------------
            if f_type in ("section", "sections"):
                raw_section_ids = (
                    f.get("ids")
                    or f.get("section_ids")
                    or []
                )
                section_ids = CatalogService._normalize_id_list(raw_section_ids)

                if raw_section_ids and not section_ids:
                    return qs.none()

                if section_ids:
                    section_ids = CatalogService._get_section_ids_with_descendants(
                        section_ids,
                    )

                    if not section_ids:
                        return qs.none()

                    product_sections = Product.sections.through.objects.filter(
                        product_id=OuterRef("pk"),
                        section_id__in=section_ids,
                    )

                    qs = qs.filter(
                        Exists(product_sections),
                    )

            # -------------------------
            # CHOICE
            # -------------------------
            elif f_type == "choice":
                raw_option_ids = f.get("option_ids") or []
                option_ids = CatalogService._normalize_id_list(raw_option_ids)

                if raw_attribute_id and not attribute_id:
                    return qs.none()

                if raw_option_ids and not option_ids:
                    return qs.none()

                if attribute_id and option_ids:
                    qs = CatalogService._filter_by_attribute_exists(
                        qs,
                        attribute_id,
                        option_id__in=option_ids,
                    )

            # -------------------------
            # NUMBER
            # -------------------------
            elif f_type == "number":
                if not attribute_id:
                    if raw_attribute_id:
                        return qs.none()
                    continue

                raw_gte = f.get("gte")
                raw_lte = f.get("lte")
                gte = CatalogService._normalize_number(raw_gte)
                lte = CatalogService._normalize_number(raw_lte)

                if raw_gte is not None and gte is None:
                    return qs.none()

                if raw_lte is not None and lte is None:
                    return qs.none()

                number_filter = {}

                if gte is not None:
                    number_filter["value_number__gte"] = gte

                if lte is not None:
                    number_filter["value_number__lte"] = lte

                qs = CatalogService._filter_by_attribute_exists(
                    qs,
                    attribute_id,
                    **number_filter,
                )

            # -------------------------
            # BOOLEAN
            # -------------------------
            elif f_type in CatalogService.BOOLEAN_TYPES:
                raw_value = f.get("value")
                value = CatalogService._normalize_bool(raw_value)

                if raw_attribute_id and not attribute_id:
                    return qs.none()

                if raw_value is not None and value is None:
                    return qs.none()

                if attribute_id and value is not None:
                    qs = CatalogService._filter_by_attribute_exists(
                        qs,
                        attribute_id,
                        value_bool=value,
                    )

            # -------------------------
            # MANUFACTURER
            # -------------------------
            elif f_type == "manufacturer":
                raw_manufacturer_ids = f.get("ids") or []
                manufacturer_ids = CatalogService._normalize_id_list(
                    raw_manufacturer_ids,
                )

                if raw_manufacturer_ids and not manufacturer_ids:
                    return qs.none()

                if manufacturer_ids:
                    qs = qs.filter(
                        manufacturer_id__in=manufacturer_ids,
                    )

            # -------------------------
            # PRICE
            # -------------------------
            elif f_type == "price":
                raw_gte = f.get("gte")
                raw_lte = f.get("lte")
                gte = CatalogService._normalize_number(raw_gte)
                lte = CatalogService._normalize_number(raw_lte)

                if raw_gte is not None and gte is None:
                    return qs.none()

                if raw_lte is not None and lte is None:
                    return qs.none()

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
                raw_value = f.get("value")
                value = CatalogService._normalize_bool(raw_value)

                if raw_value is not None and value is None:
                    return qs.none()

                if value is True:
                    qs = qs.filter(
                        discount_price__isnull=False,
                    )

                elif value is False:
                    qs = qs.filter(
                        discount_price__isnull=True,
                    )

        return qs

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
                When(
                    is_bestseller=True,
                    priority__isnull=False,
                    then=Value(1),
                ),
                When(
                    is_bestseller=True,
                    priority__isnull=True,
                    then=Value(2),
                ),
                When(
                    is_bestseller=False,
                    priority__isnull=False,
                    then=Value(3),
                ),
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
    def get_sections_tree(products_qs):
        """
        Дерево разделов для filters API.

        Важно:
        - sections отдаём всегда;
        - вложенность любая;
        - разделы без товаров не скрываем;
        - products_count считается с учётом всех потомков.
        """

        section_rows = list(
            Section.objects
            .filter(is_active=True)
            .values(
                "id",
                "name",
                "slug",
                "parent_id",
                "ordering",
            )
            .order_by(
                "parent_id",
                "ordering",
                "name",
            )
        )

        product_section_rows = (
            products_qs
            .order_by()
            .filter(sections__isnull=False)
            .values_list(
                "sections__id",
                "id",
            )
            .distinct()
        )

        direct_product_ids_by_section = defaultdict(set)

        for section_id, product_id in product_section_rows:
            if section_id:
                direct_product_ids_by_section[section_id].add(product_id)

        sections_by_id = {}

        for row in section_rows:
            sections_by_id[row["id"]] = {
                "id": row["id"],
                "name": row["name"],
                "slug": row["slug"],
                "products_count": 0,
                "children": [],
                "_parent_id": row["parent_id"],
                "_ordering": row["ordering"],
            }

        roots = []

        for section in sections_by_id.values():
            parent_id = section["_parent_id"]

            if parent_id and parent_id in sections_by_id:
                sections_by_id[parent_id]["children"].append(section)
            else:
                roots.append(section)

        def sort_sections(items):
            items.sort(
                key=lambda item: (
                    item["_ordering"],
                    item["name"],
                )
            )

            for item in items:
                sort_sections(item["children"])

        def fill_products_count(section, visited_ids=None):
            if visited_ids is None:
                visited_ids = set()

            section_id = section["id"]

            if section_id in visited_ids:
                return set()

            visited_ids.add(section_id)

            product_ids = set(
                direct_product_ids_by_section.get(
                    section_id,
                    set(),
                )
            )

            for child in section["children"]:
                product_ids.update(
                    fill_products_count(
                        child,
                        visited_ids.copy(),
                    )
                )

            section["products_count"] = len(product_ids)

            return product_ids

        def cleanup(section):
            section.pop("_parent_id", None)
            section.pop("_ordering", None)

            for child in section["children"]:
                cleanup(child)

        sort_sections(roots)

        for root in roots:
            fill_products_count(root)
            cleanup(root)

        return roots

    @staticmethod
    def get_available_filters(products_qs):
        """
        Динамическая выдача доступных фильтров.

        На вход получает queryset товаров после фильтрации.
        На выход отдаёт:
        - sections всегда;
        - price всегда;
        - has_discount всегда;
        - manufacturers только если есть;
        - attributes только если есть.
        """

        products_qs = products_qs.annotate(
            actual_price=Coalesce(
                "discount_price",
                "price",
                output_field=IntegerField(),
            )
        )

        # -------------------------
        # SECTIONS TREE
        # -------------------------
        sections = CatalogService.get_sections_tree(products_qs)

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
        product_ids = products_qs.order_by().values("id")

        attribute_values_qs = ProductAttributeValue.objects.filter(
            product_id__in=product_ids,
        )

        attribute_fields = (
            "attribute_id",
            "attribute__name",
            "attribute__slug",
            "attribute__type",
            "attribute__unit",
            "attribute__allow_multiple",
        )

        attribute_counts = {
            item["attribute_id"]: item["products_count"]
            for item in (
                attribute_values_qs
                .values("attribute_id")
                .annotate(products_count=Count("product_id", distinct=True))
            )
        }

        attributes_map = {}

        def get_attribute_data(row):
            return attributes_map.setdefault(
                row["attribute_id"],
                {
                    "id": row["attribute_id"],
                    "name": row["attribute__name"],
                    "slug": row["attribute__slug"],
                    "type": row["attribute__type"],
                    "unit": row["attribute__unit"],
                    "allow_multiple": row["attribute__allow_multiple"],
                    "products_count": attribute_counts.get(
                        row["attribute_id"],
                        0,
                    ),
                }
            )

        # -------------------------
        # CHOICE
        # -------------------------
        choice_rows = (
            attribute_values_qs
            .filter(
                attribute__type="choice",
                option__isnull=False,
                option__is_active=True,
            )
            .values(
                *attribute_fields,
                "option_id",
                "option__value",
                "option__slug",
            )
            .annotate(products_count=Count("product_id", distinct=True))
            .order_by("attribute__name", "option__value")
        )

        for row in choice_rows:
            attribute_data = get_attribute_data(row)
            options = attribute_data.setdefault("options", [])

            options.append(
                {
                    "id": row["option_id"],
                    "value": row["option__value"],
                    "slug": row["option__slug"],
                    "products_count": row["products_count"],
                }
            )

        # -------------------------
        # NUMBER
        # -------------------------
        number_rows = (
            attribute_values_qs
            .filter(
                attribute__type="number",
                value_number__isnull=False,
            )
            .values(*attribute_fields)
            .annotate(
                min=Min("value_number"),
                max=Max("value_number"),
                products_count=Count("product_id", distinct=True),
            )
            .order_by("attribute__name")
        )

        for row in number_rows:
            attribute_data = get_attribute_data(row)

            attribute_data["min"] = row["min"]
            attribute_data["max"] = row["max"]
            attribute_data["products_count"] = row["products_count"]

        # -------------------------
        # BOOLEAN
        # -------------------------
        bool_rows = (
            attribute_values_qs
            .filter(
                attribute__type__in=CatalogService.BOOLEAN_TYPES,
                value_bool__isnull=False,
            )
            .values(
                *attribute_fields,
                "value_bool",
            )
            .annotate(products_count=Count("product_id", distinct=True))
            .order_by("attribute__name", "-value_bool")
        )

        for row in bool_rows:
            attribute_data = get_attribute_data(row)
            values = attribute_data.setdefault("values", [])

            values.append(
                {
                    "value": row["value_bool"],
                    "products_count": row["products_count"],
                }
            )

        attributes = sorted(
            attributes_map.values(),
            key=lambda item: item["name"],
        )

        result = {
            "sections": sections,
            "price": {
                "min": price_data["min_price"],
                "max": price_data["max_price"],
            },
            "has_discount": has_discount,
        }

        if manufacturers:
            result["manufacturers"] = manufacturers

        if attributes:
            result["attributes"] = attributes

        return result
