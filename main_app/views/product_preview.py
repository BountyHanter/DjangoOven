from django.db.models import F, When, Case, DecimalField, BooleanField, Value, Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models import Product, Section
from main_app.serializers.product_preview import ProductPreviewSerializer
from main_app.views.utils.section_children import get_section_with_children

SORT_POPULAR = "popular"
SORT_PRICE_ASC = "price_asc"
SORT_PRICE_DESC = "price_desc"

class ProductCatalogAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductPreviewSerializer

    def get_queryset(self):

        queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("manufacturer")
            .prefetch_related(
                "images",
                "sections__parent",
            )
        )

        # --- Аннотация финальной цены ---
        queryset = queryset.annotate(
            final_price=Case(
                When(discount_price__isnull=False, then=F("discount_price")),
                default=F("price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        # --- Аннотация наличия видео ---
        queryset = queryset.annotate(
            has_video=Case(
                When(
                    Q(video_url__isnull=False) & ~Q(video_url=""),
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        # --- Поиск ---
        search_query = self.request.query_params.get("search")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            )

        # --- Фильтр по разделам ---
        section_ids = self.request.query_params.getlist("section")

        if section_ids:

            sections = Section.objects.filter(
                id__in=section_ids,
                is_active=True
            )

            all_section_ids = []

            # берём раздел + всех его потомков
            for section in sections:
                all_section_ids.extend(section.get_descendants_ids())

            queryset = queryset.filter(
                sections__id__in=all_section_ids
            ).distinct()

        # --- Фильтр по производителям ---
        manufacturer_ids = self.request.query_params.getlist("manufacturer")

        if manufacturer_ids:
            queryset = queryset.filter(
                manufacturer__id__in=manufacturer_ids,
                manufacturer__is_active=True
            )

        # --- Цена ---
        price_from = self.request.query_params.get("price_from")
        price_to = self.request.query_params.get("price_to")

        if price_from:
            queryset = queryset.filter(final_price__gte=price_from)

        if price_to:
            queryset = queryset.filter(final_price__lte=price_to)

        # --- Скидка ---
        discount = self.request.query_params.get("discount")

        if discount:
            queryset = queryset.filter(discount_price__isnull=False)

        # --- Авто-фильтры по полям Product (игнорируем неизвестные параметры) ---
        def _parse_bool(val: str):
            v = (val or "").strip().lower()
            if v in {"1", "true", "t", "yes", "y", "on"}:
                return True
            if v in {"0", "false", "f", "no", "n", "off"}:
                return False
            return None

        product_fields = {
            f.name: f
            for f in Product._meta.get_fields()
            if getattr(f, "concrete", False) and not getattr(f, "is_relation", False)
        }

        ignored_params = {
            "search",
            "ordering",
            "section",
            "manufacturer",
            "price_from",
            "price_to",
            "discount",
            "page",
            "page_size",
        }

        for param in self.request.query_params:
            if param in ignored_params:
                continue

            field = product_fields.get(param)
            if not field:
                continue

            values = self.request.query_params.getlist(param)
            if not values:
                continue

            # для boolean аккуратно приводим значения
            if isinstance(field, BooleanField):
                parsed = []
                for v in values:
                    b = _parse_bool(v)
                    if b is not None:
                        parsed.append(b)

                if parsed:
                    queryset = queryset.filter(**{f"{param}__in": parsed})

            else:
                queryset = queryset.filter(**{f"{param}__in": values})

        # --- Сортировка ---
        ordering = self.request.query_params.get("ordering")

        if ordering == SORT_POPULAR:
            queryset = queryset.order_by("-is_popular", "-created_at")

        elif ordering == SORT_PRICE_DESC:
            queryset = queryset.order_by("-final_price", "-created_at")

        elif ordering == SORT_PRICE_ASC:
            queryset = queryset.order_by("final_price", "-created_at")

        else:
            # Авто-сортировка по любому полю Product: ordering=field или ordering=-field
            allowed_order_fields = set(product_fields.keys()) | {"final_price", "has_video"}

            if ordering:
                field_name = ordering[1:] if ordering.startswith("-") else ordering
                if field_name in allowed_order_fields:
                    queryset = queryset.order_by(ordering, "-created_at")
                else:
                    queryset = queryset.order_by("-created_at")
            else:
                queryset = queryset.order_by("-created_at")

        return queryset