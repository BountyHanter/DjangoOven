from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from django.db.models import Case, When, F, DecimalField, BooleanField, Value, Q

from main_app.models import Product
from main_app.serializers.product_detail import ProductDetailSerializer


class ProductDetailAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    lookup_field = "id"

    def get_queryset(self):

        return (
            Product.objects
            .filter(is_active=True)
            .select_related("manufacturer")
            .prefetch_related(
                "images",
                "documents",
                "sections__parent",
            )
            .annotate(
                final_price=Case(
                    When(discount_price__isnull=False, then=F("discount_price")),
                    default=F("price"),
                    output_field=DecimalField(max_digits=12, decimal_places=2)
                ),
            )
        )
