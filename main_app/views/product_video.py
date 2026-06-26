from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models import ProductVideo
from main_app.serializers.product_video import ProductVideoSerializer


class ProductVideoListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductVideoSerializer
    pagination_class = None

    def get_queryset(self):
        return ProductVideo.objects.filter(
            product_id=self.kwargs["product_id"],
            product__is_active=True,
        )
