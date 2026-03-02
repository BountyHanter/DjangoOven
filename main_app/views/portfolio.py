from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models import Portfolio, Section
from main_app.serializers.portfolio import PortfolioSerializer



class PortfolioListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        queryset = (
            Portfolio.objects
            .select_related("product")
            .prefetch_related("images")
            .order_by("-created_at")
        )

        product_id = (
            self.kwargs.get("product_id")
            or self.request.query_params.get("product")
        )

        section_id = self.request.query_params.get("section")
        main = self.request.query_params.get("main")
        manufacturer_ids = self.request.query_params.get("manufacturer")

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        # ✅ ФИЛЬТР С ДОЧЕРНИМИ РАЗДЕЛАМИ
        if section_id:
            section = Section.objects.get(id=section_id)
            section_ids = section.get_descendants_ids()

            queryset = queryset.filter(
                product__sections__id__in=section_ids
            )

        if manufacturer_ids:
            queryset = queryset.filter(
                product__manufacturer_id__in=manufacturer_ids
            )

        if main == "true":
            queryset = queryset.filter(main=True)

        return queryset.distinct()