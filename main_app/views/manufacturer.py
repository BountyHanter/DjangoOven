from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from main_app.models import Manufacturer
from main_app.serializers.manufacturer import ManufacturerPreviewSerializer, ManufacturerDetailSerializer
from main_app.views.utils.manufacturer_sort import sort_manufacturers


class ManufacturerPreviewListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ManufacturerPreviewSerializer

    def get_queryset(self):
        queryset = Manufacturer.objects.filter(is_active=True)

        ordering = self.request.query_params.get("ordering")

        # сортировка по приоритету
        if ordering == "priority":
            return queryset.order_by("-priority", "name")

        return sort_manufacturers(queryset)


class ManufacturerDetailAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ManufacturerDetailSerializer
    queryset = Manufacturer.objects.filter(is_active=True)
    lookup_field = "id"
