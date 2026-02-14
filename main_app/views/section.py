from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.models import Manufacturer, FUEL_TYPE_CHOICES
from main_app.models.section import Section
from main_app.serializers.section import SectionTreeSerializer
from main_app.serializers.manufacturer import ManufacturerSerializer


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

        fuel_types = [
            {
                "value": value,
                "label": label
            }
            for value, label in FUEL_TYPE_CHOICES
        ]

        return Response({
            "sections": SectionTreeSerializer(sections, many=True).data,
            "manufacturers": ManufacturerSerializer(manufacturers, many=True).data,
            "fuel_types": fuel_types,
        })