import json

from json import JSONDecodeError

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app.services.catalog.service import CatalogService


class CatalogFiltersAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = self._parse_filters(request)

        if filters is None:
            return Response(
                {
                    "detail": "Некорректный формат filters. Ожидается JSON-список."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = CatalogService.get_filters_data(filters)

        return Response(data)

    @staticmethod
    def _parse_filters(request):
        raw_filters = request.query_params.get("filters")

        if not raw_filters:
            return []

        try:
            filters = json.loads(raw_filters)
        except JSONDecodeError:
            return None

        if not isinstance(filters, list):
            return None

        return filters