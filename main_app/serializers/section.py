from django.db.models import Count, Q
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

        return (
            Product.objects
            .filter(
                is_active=True,
                sections__id__in=section_ids
            )
            .distinct()
            .count()
        )

    def get_children(self, obj):

        children = obj.children.filter(
            is_active=True
        ).order_by("ordering", "name")

        return SectionTreeSerializer(children, many=True).data