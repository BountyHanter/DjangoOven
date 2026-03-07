from rest_framework import serializers

from main_app.models import ProductDocument, ProductImage, Section, Manufacturer, Product
from main_app.serializers.mixin import ChoicesDisplayMixin


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ("id", "name")

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
    sections = serializers.SerializerMethodField()

    images = ProductImageSerializer(many=True)
    documents = ProductDocumentSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"

    def get_sections(self, obj):
        result = []

        for section in obj.sections.all():
            path = section.get_path()

            result.append([
                {
                    "id": s.id,
                    "name": s.name,
                    "slug": s.slug,
                }
                for s in path
            ])

        return result
