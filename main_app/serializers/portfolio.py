from rest_framework import serializers
from main_app.models import Portfolio, PortfolioImage


class PortfolioImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioImage
        fields = ("id", "image", "order")


class PortfolioSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    images = PortfolioImageSerializer(many=True, read_only=True)

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
            "type_work",
            "product_id",
            "product_name",
            "images",
            "created_at",
        )