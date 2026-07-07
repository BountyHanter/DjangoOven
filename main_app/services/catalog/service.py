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
from main_app.models.attribute import (
    ProductAttribute,
    ProductAttributeOption,
    ProductAttributeValue,
)
from main_app.models.manufacturer import Manufacturer
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
    def get_products_queryset(
        filters: list[dict] | None = None,
        ordering: str | None = None,
    ):
        """
        Базовая выдача товаров каталога:
        - только активные товары
        - применяем фильтры
        - применяем сортировку

        Пагинацию здесь НЕ делаем.
        """

        qs = CatalogService.apply_filters(filters or [])
        qs = CatalogService.apply_sorting(qs, ordering)

        return qs

    @staticmethod
    def get_products_page(
        request,
        filters: list[dict] | None = None,
        ordering: str | None = None,
    ):
        """
        Базовая выдача товаров с пагинацией.
        """

        qs = CatalogService.get_products_queryset(filters, ordering)

        paginator = DefaultPagination()
        page = paginator.paginate_queryset(qs, request)

        return {
            "paginator": paginator,
            "page": page,
            "queryset": qs,
        }

    @staticmethod
    def get_preview_products_queryset(
        filters: list[dict] | None = None,
        ordering: str | None = None,
        search: str | None = None,
    ):
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
        qs = CatalogService.apply_search(qs, search)
        qs = CatalogService.prepare_preview_queryset(qs)
        qs = CatalogService.apply_sorting(qs, ordering)

        return qs

    @staticmethod
    def get_preview_products_page(
        request,
        filters: list[dict] | None = None,
        ordering: str | None = None,
        search: str | None = None,
    ):
        """
        Preview-выдача товаров с пагинацией.
        """

        qs = CatalogService.get_preview_products_queryset(
            filters,
            ordering,
            search,
        )

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

        filters = filters or []
        qs = CatalogService.apply_filters(filters)

        return CatalogService.get_available_filters(qs, filters)

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
            # RANGE
            # -------------------------
            elif f_type == "range":
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

                range_filter = {
                    "value_number_from__isnull": False,
                    "value_number_to__isnull": False,
                }

                if gte is not None:
                    range_filter["value_number_to__gte"] = gte

                if lte is not None:
                    range_filter["value_number_from__lte"] = lte

                qs = CatalogService._filter_by_attribute_exists(
                    qs,
                    attribute_id,
                    **range_filter,
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
    def _selected_multi_choice_attribute_ids(filters: list[dict]):
        choice_attribute_ids = []

        for f in filters:
            if f.get("type") != "choice":
                continue

            attribute_id = CatalogService._normalize_id(
                f.get("attribute_id"),
            )
            option_ids = CatalogService._normalize_id_list(
                f.get("option_ids") or [],
            )

            if attribute_id and option_ids:
                choice_attribute_ids.append(attribute_id)

        if not choice_attribute_ids:
            return set()

        return set(
            ProductAttribute.objects.filter(
                id__in=choice_attribute_ids,
                type=ProductAttribute.AttributeType.CHOICE,
                allow_multiple=True,
                hide_in_filter=False,
            ).values_list("id", flat=True)
        )

    @staticmethod
    def _selected_choice_option_ids_by_attribute(filters: list[dict]):
        selected_options = defaultdict(list)

        for f in filters:
            if f.get("type") != "choice":
                continue

            attribute_id = CatalogService._normalize_id(
                f.get("attribute_id"),
            )
            option_ids = CatalogService._normalize_id_list(
                f.get("option_ids") or [],
            )

            if not attribute_id or not option_ids:
                continue

            for option_id in option_ids:
                if option_id not in selected_options[attribute_id]:
                    selected_options[attribute_id].append(option_id)

        return selected_options

    @staticmethod
    def _filters_without_choice_attribute(filters: list[dict], attribute_id: int):
        return [
            f
            for f in filters
            if not (
                f.get("type") == "choice"
                and CatalogService._normalize_id(
                    f.get("attribute_id"),
                ) == attribute_id
            )
        ]

    @staticmethod
    def _selected_number_attribute_ids(filters: list[dict]):
        number_attribute_ids = []

        for f in filters:
            if f.get("type") != "number":
                continue

            attribute_id = CatalogService._normalize_id(
                f.get("attribute_id"),
            )
            has_range = f.get("gte") is not None or f.get("lte") is not None

            if attribute_id and has_range:
                number_attribute_ids.append(attribute_id)

        if not number_attribute_ids:
            return set()

        return set(
            ProductAttribute.objects.filter(
                id__in=number_attribute_ids,
                type=ProductAttribute.AttributeType.NUMBER,
                hide_in_filter=False,
            ).values_list("id", flat=True)
        )

    @staticmethod
    def _filters_without_number_attribute(filters: list[dict], attribute_id: int):
        return [
            f
            for f in filters
            if not (
                f.get("type") == "number"
                and CatalogService._normalize_id(
                    f.get("attribute_id"),
                ) == attribute_id
            )
        ]

    @staticmethod
    def _selected_range_attribute_ids(filters: list[dict]):
        range_attribute_ids = []

        for f in filters:
            if f.get("type") != "range":
                continue

            attribute_id = CatalogService._normalize_id(
                f.get("attribute_id"),
            )
            has_range = f.get("gte") is not None or f.get("lte") is not None

            if attribute_id and has_range:
                range_attribute_ids.append(attribute_id)

        if not range_attribute_ids:
            return set()

        return set(
            ProductAttribute.objects.filter(
                id__in=range_attribute_ids,
                type=ProductAttribute.AttributeType.RANGE,
                hide_in_filter=False,
            ).values_list("id", flat=True)
        )

    @staticmethod
    def _filters_without_range_attribute(filters: list[dict], attribute_id: int):
        return [
            f
            for f in filters
            if not (
                f.get("type") == "range"
                and CatalogService._normalize_id(
                    f.get("attribute_id"),
                ) == attribute_id
            )
        ]

    @staticmethod
    def _selected_manufacturer_ids(filters: list[dict]):
        manufacturer_ids = []

        for f in filters:
            if f.get("type") != "manufacturer":
                continue

            manufacturer_ids.extend(
                CatalogService._normalize_id_list(
                    f.get("ids") or [],
                )
            )

        return manufacturer_ids

    @staticmethod
    def _has_selected_manufacturer_filter(filters: list[dict]):
        return bool(CatalogService._selected_manufacturer_ids(filters))

    @staticmethod
    def _filters_without_manufacturer(filters: list[dict]):
        return [
            f
            for f in filters
            if f.get("type") != "manufacturer"
        ]

    @staticmethod
    def apply_search(qs, search: str | None = None):
        if not search:
            return qs

        search_query = search.strip()

        if not search_query:
            return qs

        return qs.filter(name__icontains=search_query)

    @staticmethod
    def apply_sorting(qs, ordering: str | None = None):
        """
        Сортировка каталога:

        Если ordering не передан, используется сортировка по популярности:
        1. хит + приоритет
        2. хит без приоритета
        3. приоритет без хита
        4. остальное

        Внутри приоритетных групп:
        - priority ASC, потому что 1 — самый высокий приоритет

        Если товары одинаковые по группе/приоритету:
        - created_at DESC
        """

        if ordering == "newest":
            return qs.order_by("-created_at")

        if ordering in {"price_asc", "price_desc"}:
            qs = qs.annotate(
                actual_price=Coalesce(
                    "discount_price",
                    "price",
                    output_field=IntegerField(),
                )
            )

            if ordering == "price_asc":
                return qs.order_by("actual_price", "-created_at")

            return qs.order_by("-actual_price", "-created_at")

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
        - count считается с учётом всех потомков.
        """

        section_rows = list(
            Section.objects
            .filter(is_active=True)
            .only(
                "id",
                "name",
                "slug",
                "parent",
                "description_main",
                "image",
                "browser_title",
                "description",
                "meta_description",
                "meta_keywords",
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

        for section in section_rows:
            sections_by_id[section.id] = {
                "id": section.id,
                "name": section.name,
                "slug": section.slug,
                "description_main": section.description_main,
                "image": section.image.url if section.image else None,
                "browser_title": section.browser_title,
                "description": section.description,
                "meta_description": section.meta_description,
                "meta_keywords": section.meta_keywords,
                "ordering": section.ordering,
                "count": 0,
                "children": [],
                "_parent_id": section.parent_id,
                "_ordering": section.ordering,
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

            section["count"] = len(product_ids)

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
    def _filter_priority_sort_key(item):
        priority = item.get("_priority") or 0

        return (
            priority == 0,
            priority,
            item["id"],
        )

    @staticmethod
    def _sort_filter_attributes(attributes):
        sorted_attributes = sorted(
            attributes,
            key=CatalogService._filter_priority_sort_key,
        )

        for attribute in sorted_attributes:
            if "options" in attribute:
                attribute["options"] = sorted(
                    attribute["options"],
                    key=CatalogService._filter_priority_sort_key,
                )

                for option in attribute["options"]:
                    option.pop("_priority", None)

            attribute.pop("_priority", None)

        return sorted_attributes

    @staticmethod
    def get_available_filters(products_qs, filters: list[dict] | None = None):
        """
        Динамическая выдача доступных фильтров.

        На вход получает queryset товаров после фильтрации.
        На выход отдаёт:
        - sections всегда;
        - price всегда;
        - has_discount и has_discount_count всегда;
        - manufacturers только если есть;
        - attributes только если есть.
        """

        filters = filters or []
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
        has_discount_count = products_qs.filter(
            discount_price__isnull=False,
        ).count()
        has_discount = has_discount_count > 0

        # -------------------------
        # MANUFACTURERS
        # -------------------------
        manufacturer_products_qs = products_qs

        if CatalogService._has_selected_manufacturer_filter(filters):
            manufacturer_products_qs = CatalogService.apply_filters(
                CatalogService._filters_without_manufacturer(filters),
            )

        manufacturers_qs = (
            manufacturer_products_qs
            .filter(
                manufacturer__isnull=False,
                manufacturer__is_active=True,
            )
            .values(
                "manufacturer_id",
                "manufacturer__name",
                "manufacturer__slug",
                "manufacturer__logo",
                "manufacturer__priority",
            )
            .annotate(
                products_count=Count("id", distinct=True),
            )
            .order_by("-manufacturer__priority", "manufacturer__name")
        )

        manufacturers = [
            {
                "id": item["manufacturer_id"],
                "name": item["manufacturer__name"],
                "slug": item["manufacturer__slug"],
                "logo": item["manufacturer__logo"],
                "_priority": item["manufacturer__priority"],
                "products_count": item["products_count"],
            }
            for item in manufacturers_qs
        ]
        manufacturer_ids = {
            manufacturer["id"]
            for manufacturer in manufacturers
        }
        missing_selected_manufacturer_ids = [
            manufacturer_id
            for manufacturer_id in CatalogService._selected_manufacturer_ids(filters)
            if manufacturer_id not in manufacturer_ids
        ]

        if missing_selected_manufacturer_ids:
            selected_manufacturers = (
                Manufacturer.objects
                .filter(
                    id__in=missing_selected_manufacturer_ids,
                    is_active=True,
                )
                .values(
                    "id",
                    "name",
                    "slug",
                    "logo",
                    "priority",
                )
            )

            manufacturers.extend(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "slug": item["slug"],
                    "logo": item["logo"],
                    "_priority": item["priority"],
                    "products_count": 0,
                }
                for item in selected_manufacturers
            )

            manufacturers.sort(
                key=lambda item: (
                    -item["_priority"],
                    item["name"],
                )
            )

        for manufacturer in manufacturers:
            manufacturer.pop("_priority", None)

        # -------------------------
        # ATTRIBUTES
        # -------------------------
        product_ids = products_qs.order_by().values("id")

        attribute_values_qs = ProductAttributeValue.objects.filter(
            product_id__in=product_ids,
            attribute__hide_in_filter=False,
        )

        attribute_fields = (
            "attribute_id",
            "attribute__name",
            "attribute__slug",
            "attribute__type",
            "attribute__unit",
            "attribute__allow_multiple",
            "attribute__priority",
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
                    "_priority": row["attribute__priority"],
                    "products_count": attribute_counts.get(
                        row["attribute_id"],
                        0,
                    ),
                }
            )

        # -------------------------
        # CHOICE
        # -------------------------
        selected_multi_choice_attribute_ids = (
            CatalogService._selected_multi_choice_attribute_ids(filters)
        )
        selected_choice_option_ids_by_attribute = (
            CatalogService._selected_choice_option_ids_by_attribute(filters)
        )
        added_choice_option_ids_by_attribute = defaultdict(set)

        def append_choice_rows(rows):
            for row in rows:
                attribute_data = get_attribute_data(row)
                options = attribute_data.setdefault("options", [])
                added_choice_option_ids_by_attribute[
                    row["attribute_id"]
                ].add(row["option_id"])

                options.append(
                    {
                        "id": row["option_id"],
                        "value": row["option__value"],
                        "slug": row["option__slug"],
                        "_priority": row["option__priority"],
                        "products_count": row["products_count"],
                    }
                )

        choice_values_qs = attribute_values_qs.filter(
            attribute__type=ProductAttribute.AttributeType.CHOICE,
            option__isnull=False,
            option__is_active=True,
        )

        if selected_multi_choice_attribute_ids:
            choice_values_qs = choice_values_qs.exclude(
                attribute_id__in=selected_multi_choice_attribute_ids,
            )

        choice_rows = (
            choice_values_qs
            .values(
                *attribute_fields,
                "option_id",
                "option__value",
                "option__slug",
                "option__priority",
            )
            .annotate(products_count=Count("product_id", distinct=True))
            .order_by("attribute_id", "option_id")
        )

        append_choice_rows(choice_rows)

        for attribute_id in selected_multi_choice_attribute_ids:
            facet_filters = CatalogService._filters_without_choice_attribute(
                filters,
                attribute_id,
            )
            facet_product_ids = (
                CatalogService.apply_filters(facet_filters)
                .order_by()
                .values("id")
            )

            facet_choice_rows = (
                ProductAttributeValue.objects
                .filter(
                    product_id__in=facet_product_ids,
                    attribute_id=attribute_id,
                    attribute__hide_in_filter=False,
                    attribute__type=ProductAttribute.AttributeType.CHOICE,
                    option__isnull=False,
                    option__is_active=True,
                )
                .values(
                    *attribute_fields,
                    "option_id",
                    "option__value",
                    "option__slug",
                    "option__priority",
                )
                .annotate(products_count=Count("product_id", distinct=True))
                .order_by("attribute_id", "option_id")
            )

            append_choice_rows(facet_choice_rows)

        missing_selected_option_ids_by_attribute = defaultdict(list)

        for (
            attribute_id,
            option_ids,
        ) in selected_choice_option_ids_by_attribute.items():
            added_option_ids = added_choice_option_ids_by_attribute[attribute_id]

            for option_id in option_ids:
                if option_id not in added_option_ids:
                    missing_selected_option_ids_by_attribute[attribute_id].append(
                        option_id,
                    )

        for (
            attribute_id,
            option_ids,
        ) in missing_selected_option_ids_by_attribute.items():
            selected_options = (
                ProductAttributeOption.objects.filter(
                    attribute_id=attribute_id,
                    id__in=option_ids,
                    is_active=True,
                    attribute__type=ProductAttribute.AttributeType.CHOICE,
                    attribute__hide_in_filter=False,
                )
                .select_related("attribute")
            )

            for option in selected_options:
                attribute = option.attribute
                attribute_data = attributes_map.setdefault(
                    attribute.id,
                    {
                        "id": attribute.id,
                        "name": attribute.name,
                        "slug": attribute.slug,
                        "type": attribute.type,
                        "unit": attribute.unit,
                        "allow_multiple": attribute.allow_multiple,
                        "_priority": attribute.priority,
                        "products_count": attribute_counts.get(
                            attribute.id,
                            0,
                        ),
                    },
                )
                options = attribute_data.setdefault("options", [])

                options.append(
                    {
                        "id": option.id,
                        "value": option.value,
                        "slug": option.slug,
                        "_priority": option.priority,
                        "products_count": 0,
                    }
                )

        # -------------------------
        # NUMBER
        # -------------------------
        selected_number_attribute_ids = (
            CatalogService._selected_number_attribute_ids(filters)
        )

        def apply_number_row(row):
            attribute_data = get_attribute_data(row)

            attribute_data["min"] = row["min"]
            attribute_data["max"] = row["max"]
            attribute_data["products_count"] = row["products_count"]

        number_values_qs = attribute_values_qs.filter(
            attribute__type=ProductAttribute.AttributeType.NUMBER,
            value_number__isnull=False,
        )

        if selected_number_attribute_ids:
            number_values_qs = number_values_qs.exclude(
                attribute_id__in=selected_number_attribute_ids,
            )

        number_rows = (
            number_values_qs
            .values(*attribute_fields)
            .annotate(
                min=Min("value_number"),
                max=Max("value_number"),
                products_count=Count("product_id", distinct=True),
            )
            .order_by("attribute_id")
        )

        for row in number_rows:
            apply_number_row(row)

        for attribute_id in selected_number_attribute_ids:
            facet_filters = CatalogService._filters_without_number_attribute(
                filters,
                attribute_id,
            )
            facet_product_ids = (
                CatalogService.apply_filters(facet_filters)
                .order_by()
                .values("id")
            )

            facet_number_rows = (
                ProductAttributeValue.objects
                .filter(
                    product_id__in=facet_product_ids,
                    attribute_id=attribute_id,
                    attribute__hide_in_filter=False,
                    attribute__type=ProductAttribute.AttributeType.NUMBER,
                    value_number__isnull=False,
                )
                .values(*attribute_fields)
                .annotate(
                    min=Min("value_number"),
                    max=Max("value_number"),
                    products_count=Count("product_id", distinct=True),
                )
                .order_by("attribute_id")
            )

            for row in facet_number_rows:
                apply_number_row(row)

        # -------------------------
        # RANGE
        # -------------------------
        selected_range_attribute_ids = (
            CatalogService._selected_range_attribute_ids(filters)
        )

        def apply_range_row(row):
            attribute_data = get_attribute_data(row)

            attribute_data["min"] = row["min"]
            attribute_data["max"] = row["max"]
            attribute_data["products_count"] = row["products_count"]

        range_values_qs = attribute_values_qs.filter(
            attribute__type=ProductAttribute.AttributeType.RANGE,
            value_number_from__isnull=False,
            value_number_to__isnull=False,
        )

        if selected_range_attribute_ids:
            range_values_qs = range_values_qs.exclude(
                attribute_id__in=selected_range_attribute_ids,
            )

        range_rows = (
            range_values_qs
            .values(*attribute_fields)
            .annotate(
                min=Min("value_number_from"),
                max=Max("value_number_to"),
                products_count=Count("product_id", distinct=True),
            )
            .order_by("attribute_id")
        )

        for row in range_rows:
            apply_range_row(row)

        for attribute_id in selected_range_attribute_ids:
            facet_filters = CatalogService._filters_without_range_attribute(
                filters,
                attribute_id,
            )
            facet_product_ids = (
                CatalogService.apply_filters(facet_filters)
                .order_by()
                .values("id")
            )

            facet_range_rows = (
                ProductAttributeValue.objects
                .filter(
                    product_id__in=facet_product_ids,
                    attribute_id=attribute_id,
                    attribute__hide_in_filter=False,
                    attribute__type=ProductAttribute.AttributeType.RANGE,
                    value_number_from__isnull=False,
                    value_number_to__isnull=False,
                )
                .values(*attribute_fields)
                .annotate(
                    min=Min("value_number_from"),
                    max=Max("value_number_to"),
                    products_count=Count("product_id", distinct=True),
                )
                .order_by("attribute_id")
            )

            for row in facet_range_rows:
                apply_range_row(row)

        # -------------------------
        # BOOLEAN
        # -------------------------
        bool_rows = (
            attribute_values_qs
            .filter(
                attribute__type__in=CatalogService.BOOLEAN_TYPES,
                value_bool=True,
            )
            .values(
                *attribute_fields,
                "value_bool",
            )
            .annotate(products_count=Count("product_id", distinct=True))
            .order_by("attribute_id", "-value_bool")
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

        attributes = CatalogService._sort_filter_attributes(
            [
                attribute
                for attribute in attributes_map.values()
                if (
                    attribute["type"]
                    not in (
                        ProductAttribute.AttributeType.NUMBER,
                        ProductAttribute.AttributeType.RANGE,
                    )
                    or (
                        attribute.get("min") is not None
                        and attribute.get("max") is not None
                        and attribute["min"] != attribute["max"]
                    )
                )
            ],
        )

        result = {
            "sections": sections,
            "price": {
                "min": price_data["min_price"],
                "max": price_data["max_price"],
            },
            "has_discount": has_discount,
            "has_discount_count": has_discount_count,
        }

        if manufacturers:
            result["manufacturers"] = manufacturers

        if attributes:
            result["attributes"] = attributes

        return result
