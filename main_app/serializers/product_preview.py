from rest_framework import serializers

from main_app.models import Product


class ProductPreviewSerializer(serializers.ModelSerializer):
    manufacturer = serializers.SerializerMethodField()
    sections = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    has_video = serializers.BooleanField(read_only=True)
    power = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "sections",
            "manufacturer",
            "is_new",
            "is_bestseller",
            "priority",
            "has_video",
            "price",
            "discount_price",
            "power",
            "images",
        )

    def get_manufacturer(self, obj):
        if not obj.manufacturer:
            return None

        return obj.manufacturer.name

    def get_sections(self, obj):
        return [
            {
                "id": section.id,
                "name": section.name,
                "slug": section.slug,
            }
            for section in obj.sections.all()
        ]

    def get_images(self, obj):
        images = getattr(obj, "preview_images", None)

        if images is None:
            images = obj.images.all()

        result = []

        for image in images:
            item = {
                "id": image.id,
                "image": image.image.url if image.image else None,
                "ordering": image.ordering,
            }

            if image.is_main:
                item["is_main"] = True

            result.append(item)

        return result

    def get_power(self, obj):
        value = getattr(obj, "power_value", None)

        if value is None:
            return None

        data = {
            "name": getattr(obj, "power_name", None) or "Мощность",
            "slug": "moshchnost",
            "value": str(value),
        }

        unit = getattr(obj, "power_unit", None)

        if unit:
            data["unit"] = unit

        return data