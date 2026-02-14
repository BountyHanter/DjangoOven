from rest_framework import serializers

from main_app.models import ProductDocument, ProductImage, Section, Manufacturer, Product
from main_app.serializers.mixin import ChoicesDisplayMixin


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ("id", "name")

class SectionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ("id", "name", "slug")

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("image", "is_main", "ordering")

class ProductDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDocument
        fields = ("title", "file")

class ProductDetailSerializer(ChoicesDisplayMixin, serializers.ModelSerializer):

    manufacturer = ManufacturerSerializer()
    sections = SectionShortSerializer(many=True)

    images = ProductImageSerializer(many=True)
    documents = ProductDocumentSerializer(many=True)

    fuel_type_display = serializers.CharField(
        source="get_fuel_type_display",
        read_only=True
    )

    class Meta:
        model = Product
        fields = "__all__"
