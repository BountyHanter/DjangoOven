from django.db.models import Q
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models.banner import Banner
from main_app.serializers.banner import BannerSerializer


class BannerListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer

    def get_queryset(self):
        queryset = Banner.objects.all().order_by("-created_at")

        section_id = self.request.query_params.get("section")
        brand_id = self.request.query_params.get("brand")

        if section_id:
            queryset = queryset.filter(
                Q(sections__id=section_id) | Q(sections__isnull=True)
            )

        if brand_id:
            queryset = queryset.filter(
                Q(manufacturer_id=brand_id) | Q(manufacturer__isnull=True)
            )

        return queryset.distinct()