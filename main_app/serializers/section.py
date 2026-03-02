from rest_framework import serializers
from main_app.models.section import Section


class SectionTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "image",
            "browser_title",
            "description",
            "meta_description",
            "meta_keywords",
            "ordering",
            "children",
        )

    def get_children(self, obj):
        children = obj.children.filter(is_active=True).order_by("ordering", "name")
        return SectionTreeSerializer(children, many=True).data