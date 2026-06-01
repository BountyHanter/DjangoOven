from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.serializers.product_preview import ProductPreviewSerializer
from main_app.serializers.product_preview_filter import ProductFilterSerializer
from main_app.views.utils.filter_helper import get_filtered_product_queryset


class ProductCatalogAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductPreviewSerializer

    def get_queryset(self):

        serializer = ProductFilterSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        filters = serializer.validated_data

        return get_filtered_product_queryset(
            filters,
            with_related=True,
            with_ordering=True,
        )
