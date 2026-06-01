from django.db.models import Count, Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import Manufacturer
from main_app.models.section import Section
from main_app.serializers.product_preview_filter import ProductFilterSerializer
from main_app.views.utils.filter_helper import (
    generate_filters,
    get_filtered_product_queryset,
    SORTING_OPTIONS,
)
from main_app.serializers.manufacturer import ManufacturerPreviewSerializer
from main_app.serializers.section import SectionTreeSerializer
from main_app.views.utils.manufacturer_sort import sort_manufacturers


class CatalogFiltersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = ProductFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data
        products_queryset = get_filtered_product_queryset(filters)

        sections = (
            Section.objects
            .filter(is_active=True, parent__isnull=True)
            .order_by("ordering", "name")
        )

        not_empty_sections = []

        for section in sections:
            section_ids = section.get_descendants_ids()

            has_products = (
                products_queryset
                .filter(
                    sections__id__in=section_ids,
                )
                .exists()
            )

            if has_products:
                not_empty_sections.append(section)

        manufacturers = (
            Manufacturer.objects
            .filter(is_active=True)
            .annotate(
                product_count=Count(
                    "product",
                    filter=Q(product__id__in=products_queryset.values("id")),
                    distinct=True,
                )
            )
            .filter(product_count__gt=0)
        )
        manufacturers = sort_manufacturers(manufacturers)

        return Response({
            "sections": SectionTreeSerializer(
                not_empty_sections,
                many=True,
                context={"products_queryset": products_queryset},
            ).data,
            "manufacturers": ManufacturerPreviewSerializer(
                manufacturers,
                many=True,
            ).data,
            "filters": generate_filters(products_queryset),
            "sorting": SORTING_OPTIONS,
        })
