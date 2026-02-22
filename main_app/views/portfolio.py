from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models import Portfolio
from main_app.serializers.portfolio import PortfolioSerializer


class PortfolioListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        queryset = (
            Portfolio.objects
            .select_related("product")
            .order_by("-created_at")
        )

        product_id = self.kwargs.get("product_id") or \
                     self.request.query_params.get("product")

        section_id = self.request.query_params.get("section")
        main = self.request.query_params.get("main")

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        if section_id:
            queryset = queryset.filter(product__sections__id=section_id)

        if main == "true":
            queryset = queryset.filter(main=True)

        return queryset.distinct()