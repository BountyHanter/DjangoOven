from rest_framework import serializers

from main_app.models import Product, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = (
            "image",
            "is_main",
            "ordering",
        )


class ProductPreviewSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    has_video = serializers.BooleanField(read_only=True)
    sections = serializers.SerializerMethodField()

    fuel_type_display = serializers.CharField(
        source="get_fuel_type_display",
        read_only=True
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sections",
            "is_new",
            "is_popular",
            "is_bestseller",
            "has_video",
            "price",
            "price_in_euro",
            "discount_price",
            "fuel_type",
            "fuel_type_display",
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

