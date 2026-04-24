from rest_framework import serializers

from main_app.models import Product, ProductImage, Manufacturer, Section


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

        # Грузим дерево предков батчами, чтобы не вызывать запрос на каждый parent.
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

            while node_id:
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

            # Fallback на случай рассинхронизации данных.
            result.append(
                [
                    {
                        "id": s.id,
                        "name": s.name,
                        "slug": s.slug,
                    }
                    for s in section.get_path()
                ]
            )

        return result
