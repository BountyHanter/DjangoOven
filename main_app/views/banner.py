from django.db.models import Case, F, IntegerField, Q, Value, When
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from main_app.models.banner import Banner
from main_app.serializers.banner import BannerSerializer


class BannerListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BannerSerializer

    def get_queryset(self):
        queryset = Banner.objects.annotate(
            priority_sort_group=Case(
                When(priority__gt=0, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            priority_sort_value=Case(
                When(priority__gt=0, then=F("priority")),
                default=Value(0),
                output_field=IntegerField(),
            ),
        ).order_by(
            "priority_sort_group",
            "priority_sort_value",
            "-created_at",
        )

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
