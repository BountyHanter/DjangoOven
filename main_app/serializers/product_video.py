from rest_framework import serializers

from main_app.models import ProductVideo


class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = (
            "id",
            "url",
            "ordering",
        )
