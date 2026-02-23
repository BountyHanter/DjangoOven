from main_app.models import ManufacturerImage
from rest_framework import serializers
from main_app.models import Manufacturer

class ManufacturerPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = (
            "id",
            "name",
            "slug",
            "logo",
            "priority",
        )

class ManufacturerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManufacturerImage
        fields = (
            "id",
            "image",
            "ordering",
        )

class ManufacturerDetailSerializer(serializers.ModelSerializer):
    images = ManufacturerImageSerializer(many=True, read_only=True)

    class Meta:
        model = Manufacturer
        fields = (
            "id",
            "name",
            "slug",
            "logo",
            "priority",

            # SEO / контент
            "keywords",
            "short_description",
            "description",
            "video",

            # галерея
            "images",
        )