from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import Manufacturer
from main_app.models.section import Section
from main_app.views.utils.filter_helper import filters
from main_app.serializers.manufacturer import ManufacturerPreviewSerializer
from main_app.serializers.section import SectionTreeSerializer


class CatalogFiltersAPIView(APIView):
    permission_classes = [AllowAny]


    def get(self, request):

        sections = Section.objects.filter(
            is_active=True,
            parent__isnull=True
        ).order_by("ordering", "name")

        manufacturers = Manufacturer.objects.filter(
            is_active=True
        )

        return Response({
            "sections": SectionTreeSerializer(sections, many=True).data,
            "manufacturers": ManufacturerPreviewSerializer(manufacturers, many=True).data,
            "filters": filters,
        })