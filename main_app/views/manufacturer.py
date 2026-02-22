from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models import Manufacturer
from main_app.serializers.manufacturer import ManufacturerSerializer


class ManufacturerListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ManufacturerSerializer

    def get_queryset(self):
        queryset = Manufacturer.objects.filter(is_active=True)

        ordering = self.request.query_params.get("ordering")

        # сортировка по приоритету
        if ordering == "priority":
            return queryset.order_by("-priority", "name")

        # сортировка по алфавиту (по умолчанию)
        return queryset.order_by("name")