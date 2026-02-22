from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models import Review
from main_app.serializers.review import ReviewSerializer


class ReviewListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        queryset = (
            Review.objects
            .select_related("product")
            .order_by("-created_at")
        )

        product_id = self.kwargs.get("product_id")

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        return queryset