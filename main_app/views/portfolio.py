from rest_framework.generics import ListAPIView
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny

from main_app.models import Portfolio, Section
from main_app.serializers.portfolio import PortfolioSerializer



class PortfolioListAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")

        if product_id is None:
            product_id = self.request.query_params.get("product")

        section_id = self.request.query_params.get("section")
        manufacturer_ids = self._parse_int_list_param("manufacturer")

        queryset = (
            Portfolio.objects
            .select_related("product")
            .prefetch_related("images")
            .order_by("-created_at")
        )

        main = self.request.query_params.get("main")

        if product_id not in (None, ""):
            product_id = self._parse_int_param(product_id, "product")
            queryset = queryset.filter(product_id=product_id)

        if section_id not in (None, ""):
            section_id = self._parse_int_param(section_id, "section")

            try:
                section = Section.objects.get(id=section_id)
            except Section.DoesNotExist:
                raise NotFound("Раздел не найден")

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

    @staticmethod
    def _parse_int_param(value, name):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError({name: "Ожидается числовой id"})

    def _parse_int_list_param(self, name):
        raw_values = self.request.query_params.getlist(name)
        ids = []

        for raw_value in raw_values:
            for value in str(raw_value).split(","):
                value = value.strip()

                if not value:
                    continue

                try:
                    ids.append(int(value))
                except ValueError:
                    raise ValidationError({name: "Ожидается список числовых id"})

        return ids
