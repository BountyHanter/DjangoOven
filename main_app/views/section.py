from django.db.models import Count, Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import Manufacturer
from main_app.models.section import Section
from main_app.views.utils.filter_helper import generate_filters, SORTING_OPTIONS
from main_app.serializers.manufacturer import ManufacturerPreviewSerializer
from main_app.serializers.section import SectionTreeSerializer
from main_app.views.utils.manufacturer_sort import sort_manufacturers


class CatalogFiltersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        sections = (
            Section.objects
            .filter(is_active=True, parent__isnull=True)
            .order_by("ordering", "name")
        )

        manufacturers = (
            Manufacturer.objects
            .filter(is_active=True)
            .annotate(
                product_count=Count(
                    "product",
                    filter=Q(product__is_active=True)
                )
            )
        )
        manufacturers = sort_manufacturers(manufacturers)

        return Response({
            "sections": SectionTreeSerializer(sections, many=True).data,
            "manufacturers": ManufacturerPreviewSerializer(manufacturers, many=True).data,
            "filters": generate_filters(),
            "sorting": SORTING_OPTIONS,
        })
