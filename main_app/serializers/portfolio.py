from rest_framework import serializers
from main_app.models import Portfolio


class PortfolioSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Portfolio
        fields = (
            "id",
            "title",
            "main",
            "duration",
            "date",
            "object_type",
            "price",
            "video_link",
            "picture",
            "type_work",
            "product_id",
            "product_name",
            "created_at",
        )