from rest_framework import serializers

from main_app.models import Product, ProductImage, Manufacturer


class ManufacturerPreviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manufacturer
        fields = (
            "name",
        )

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = (
            "image",
            "is_main",
            "ordering",
        )


class ProductPreviewSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerPreviewSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    has_video = serializers.BooleanField(read_only=True)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sections",
            "manufacturer",
            "is_new",
            "is_bestseller",
            "has_video",
            "price",
            "discount_price",
            "power_kw",
            "images",
        )

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

