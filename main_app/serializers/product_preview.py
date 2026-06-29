from rest_framework import serializers

from main_app.models import Product, Section


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

    def _build_section_path_cache(self):
        if hasattr(self, "_section_path_cache"):
            return

        products = getattr(self.parent, "instance", None)
        section_ids = set()

        if products is not None:
            for product in products:
                for section in product.sections.all():
                    section_ids.add(section.id)

        if not section_ids:
            self._section_path_cache = {}
            return

        sections_by_id = {}
        pending_ids = set(section_ids)

        while pending_ids:
            rows = Section.objects.filter(id__in=pending_ids).values(
                "id",
                "name",
                "slug",
                "parent_id",
            )

            pending_ids = set()

            for row in rows:
                section_id = row["id"]
                sections_by_id[section_id] = row

                parent_id = row["parent_id"]
                if parent_id and parent_id not in sections_by_id:
                    pending_ids.add(parent_id)

        section_path_cache = {}

        for section_id in section_ids:
            path = []
            node_id = section_id
            visited_ids = set()

            while node_id:
                if node_id in visited_ids:
                    break

                visited_ids.add(node_id)
                node = sections_by_id.get(node_id)

                if node is None:
                    break

                path.append(
                    {
                        "id": node["id"],
                        "name": node["name"],
                        "slug": node["slug"],
                    }
                )
                node_id = node["parent_id"]

            section_path_cache[section_id] = list(reversed(path))

        self._section_path_cache = section_path_cache

    def get_sections(self, obj):
        self._build_section_path_cache()

        result = []

        for section in obj.sections.all():
            path = self._section_path_cache.get(section.id)

            if path is not None:
                result.append(path)
                continue

            result.append(
                [
                    {
                        "id": item.id,
                        "name": item.name,
                        "slug": item.slug,
                    }
                    for item in section.get_path()
                ]
            )

        return result

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
