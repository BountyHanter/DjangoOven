from rest_framework import serializers

from main_app.models import Product
from main_app.models.section import Section


class SectionTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = (
            "id",
            "name",
            "slug",
            "description_main",
            "image",
            "browser_title",
            "description",
            "meta_description",
            "meta_keywords",
            "ordering",
            "count",
            "children",
        )

    def get_count(self, obj):

        section_ids = obj.get_descendants_ids()
        products_queryset = self.context.get(
            "products_queryset",
            Product.objects.filter(is_active=True),
        )

        return (
            products_queryset
            .filter(
                sections__id__in=section_ids,
            )
            .distinct()
            .count()
        )

    def get_children(self, obj):

        children = (
            obj.children
            .filter(is_active=True)
            .order_by("ordering", "name")
        )

        not_empty_children = []
        products_queryset = self.context.get(
            "products_queryset",
            Product.objects.filter(is_active=True),
        )

        for child in children:
            section_ids = child.get_descendants_ids()

            has_products = (
                products_queryset
                .filter(
                    sections__id__in=section_ids,
                )
                .exists()
            )

            if has_products:
                not_empty_children.append(child)

        return SectionTreeSerializer(
            not_empty_children,
            many=True,
            context=self.context,
        ).data
