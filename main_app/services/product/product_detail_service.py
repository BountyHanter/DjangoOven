from django.shortcuts import get_object_or_404

from main_app.models.product import Product
from main_app.models.attribute import ProductAttributeValue


class ProductDetailService:

    @staticmethod
    def get_product(product_id: int):
        product_qs = (
            Product.objects
            .filter(is_active=True)
            .select_related("manufacturer")
            .prefetch_related(
                "images",
                "videos",
                "documents",
                "sections",
            )
        )

        product = get_object_or_404(product_qs, id=product_id)

        return {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "manufacturer": (
                product.manufacturer.name
                if product.manufacturer
                else None
            ),
            "price": product.price,
            "discount_price": product.discount_price,
            "description": product.description,
            "schema": product.schema.url if product.schema else None,
            "is_new": product.is_new,
            "is_bestseller": product.is_bestseller,
            "priority": product.priority,
            "created_at": product.created_at,
            "sections": ProductDetailService._get_sections(product),
            "images": ProductDetailService._get_images(product),
            "videos": ProductDetailService._get_videos(product),
            "documents": ProductDetailService._get_documents(product),
            "attributes": ProductDetailService._get_attributes(product.id),
        }

    @staticmethod
    def _get_sections(product):
        return [
            [
                {
                    "id": section_item.id,
                    "name": section_item.name,
                    "slug": section_item.slug,
                }
                for section_item in section.get_path()
            ]
            for section in product.sections.all()
        ]

    @staticmethod
    def _get_images(product):
        return [
            {
                "id": image.id,
                "image": image.image.url if image.image else None,
                "ordering": image.ordering,
                **({"is_main": True} if image.is_main else {})
            }
            for image in product.images.all()
        ]

    @staticmethod
    def _get_videos(product):
        return [
            {
                "id": video.id,
                "url": video.url,
                "preview_url": video.preview_url,
                "ordering": video.ordering,
            }
            for video in product.videos.all()
        ]

    @staticmethod
    def _get_documents(product):
        return [
            {
                "id": document.id,
                "title": document.title,
                "file": document.file.url if document.file else None,
                "ordering": document.ordering,
            }
            for document in product.documents.all()
        ]

    @staticmethod
    def _get_attributes(product_id: int):
        values = (
            ProductAttributeValue.objects
            .filter(product_id=product_id)
            .select_related("attribute", "option")
            .order_by("attribute__name", "id")
        )

        attributes = []
        attributes_by_id = {}

        for item in values:
            attribute = item.attribute
            value = ProductDetailService._get_attribute_value(item)

            if value is None:
                continue

            if attribute.id not in attributes_by_id:
                attribute_data = {
                    "id": attribute.id,
                    "name": attribute.name,
                    "slug": attribute.slug,
                    "type": attribute.type,
                    "value": [] if attribute.allow_multiple else value,
                }

                if attribute.unit:
                    attribute_data["unit"] = attribute.unit

                attributes_by_id[attribute.id] = attribute_data
                attributes.append(attribute_data)

            if attribute.allow_multiple:
                attributes_by_id[attribute.id]["value"].append(value)

                continue

        return attributes

    @staticmethod
    def _get_attribute_value(item):
        attribute_type = item.attribute.type

        if attribute_type == "choice":
            if not item.option:
                return None

            return {
                "id": item.option.id,
                "name": item.option.value,
                "slug": item.option.slug,
            }

        if attribute_type == "number":
            if item.value_number is None:
                return None

            return str(item.value_number)

        if attribute_type in ("bool", "boolean"):
            if item.value_bool is None:
                return None

            return item.value_bool

        if attribute_type == "text":
            if not item.value_text:
                return None

            return item.value_text

        return None
