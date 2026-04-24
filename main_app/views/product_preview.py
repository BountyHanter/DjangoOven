from django.db.models import F, When, Case, DecimalField, BooleanField, Value, Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models import Product, Section
from main_app.serializers.product_preview import ProductPreviewSerializer
from main_app.serializers.product_preview_filter import ProductFilterSerializer
from main_app.views.utils.filter_helper import FILTER_FIELDS, DEFAULT_SORTING, SORTING_MAP

class ProductCatalogAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductPreviewSerializer

    def get_queryset(self):

        serializer = ProductFilterSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data

        queryset = (
            Product.objects
            .filter(is_active=True)
            .select_related("manufacturer")
            .prefetch_related(
                "images",
                "sections",
            )
        )

        # --- финальная цена ---
        queryset = queryset.annotate(
            final_price=Case(
                When(discount_price__isnull=False, then=F("discount_price")),
                default=F("price"),
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
        )

        # --- скидка ---
        discount = filters.get("discount")

        if discount:
            queryset = queryset.filter(discount_price__isnull=False)

        # --- есть ли видео ---
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

        # --- поиск ---
        search_query = filters.get("search")

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query)
            )

        # --- разделы ---
        section_ids = filters.get("section")

        if section_ids:

            sections = Section.objects.filter(
                id__in=section_ids,
                is_active=True
            )

            all_section_ids = []

            for section in sections:
                all_section_ids.extend(section.get_descendants_ids())

            queryset = queryset.filter(
                sections__id__in=all_section_ids
            ).distinct()

        # --- производители ---
        manufacturer_ids = filters.get("manufacturer")

        if manufacturer_ids:
            queryset = queryset.filter(
                manufacturer__id__in=manufacturer_ids,
                manufacturer__is_active=True
            )

        # --- автоматические фильтры ---
        for field in FILTER_FIELDS:

            value = filters.get(field)

            if value is None:
                continue

            # select (списки)
            if isinstance(value, list):
                queryset = queryset.filter(**{f"{field}__in": value})

            # boolean / exact
            else:
                queryset = queryset.filter(**{field: value})

        # --- price range ---
        price_from = filters.get("price_from")
        price_to = filters.get("price_to")

        if price_from:
            queryset = queryset.filter(final_price__gte=price_from)

        if price_to:
            queryset = queryset.filter(final_price__lte=price_to)

        # --- power range ---
        power_kw_min = filters.get("power_kw_min")
        power_kw_max = filters.get("power_kw_max")

        if power_kw_min:
            queryset = queryset.filter(power_kw__gte=power_kw_min)

        if power_kw_max:
            queryset = queryset.filter(power_kw__lte=power_kw_max)

        # --- steam volume ---
        steam_from = filters.get("steam_volume_from")
        steam_to = filters.get("steam_volume_to")

        if steam_from is not None:
            queryset = queryset.filter(
                steam_volume_to__gte=steam_from
            )

        if steam_to is not None:
            queryset = queryset.filter(
                steam_volume_from__lte=steam_to
            )

        # --- сортировка ---
        ordering = filters.get("ordering", DEFAULT_SORTING)

        ordering_fields = SORTING_MAP.get(
            ordering,
            SORTING_MAP[DEFAULT_SORTING]
        )

        queryset = queryset.order_by(*ordering_fields)

        return queryset
