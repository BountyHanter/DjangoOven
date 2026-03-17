from rest_framework import serializers
from main_app.models.banner import Banner


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Banner
        fields = [
            "id",
            "title",
            "image",
            "link",
        ]