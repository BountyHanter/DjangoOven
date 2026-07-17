from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from main_app.serializers.product_detail import ProductDetailSerializer
from main_app.services.product.product_detail_service import ProductDetailService


class ProductDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        data = ProductDetailService.get_product(id)

        return Response(ProductDetailSerializer(data).data)
