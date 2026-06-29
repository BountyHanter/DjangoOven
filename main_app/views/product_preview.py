import json

from json import JSONDecodeError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from main_app.serializers.product_preview import ProductPreviewSerializer
from main_app.services.catalog.service import CatalogService


class ProductCatalogAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        filters = self._parse_filters(request)

        if filters is None:
            return Response(
                {
                    "detail": (
                        "Некорректный формат filters. "
                        "Ожидается JSON-список объектов."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        page_data = CatalogService.get_preview_products_page(
            request=request,
            filters=filters,
        )

        serializer = ProductPreviewSerializer(
            page_data["page"],
            many=True,
            context={"request": request},
        )

        return page_data["paginator"].get_paginated_response(
            serializer.data
        )

    @staticmethod
    def _parse_filters(request):
        raw_filters = request.query_params.get("filters")

        if not raw_filters:
            return []

        try:
            filters = json.loads(raw_filters)
        except JSONDecodeError:
            return None

        if (
            not isinstance(filters, list)
            or not all(isinstance(item, dict) for item in filters)
        ):
            return None

        return filters
