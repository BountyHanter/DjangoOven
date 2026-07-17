from rest_framework import serializers

from main_app.models import ProductVideo


class ProductVideoSerializer(serializers.ModelSerializer):
    preview = serializers.SerializerMethodField()

    class Meta:
        model = ProductVideo
        fields = (
            "id",
            "url",
            "preview",
            "ordering",
        )

    def get_preview(self, obj):
        if not obj.preview:
            return None

        return obj.preview.url
