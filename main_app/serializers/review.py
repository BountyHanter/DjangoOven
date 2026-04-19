from rest_framework import serializers
from main_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):

    product_id = serializers.IntegerField(
        source="product.id",
        read_only=True,
    )

    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "name",
            "client_name",
            "installation_time",
            "location",
            "work_description",
            "date",
            "work_description",
            "price",
            "video_url",
            "preview_image",
            "product_id",
            "product_name",
            "created_at",
        )