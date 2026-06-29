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
            "is_new": product.is_new,
            "is_bestseller": product.is_bestseller,
            "priority": product.priority,
            "created_at": product.created_at,
            "images": ProductDetailService._get_images(product),
            "videos": ProductDetailService._get_videos(product),
            "documents": ProductDetailService._get_documents(product),
            "attributes": ProductDetailService._get_attributes(product.id),
        }

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
        used_attribute_ids = set()

        for item in values:
            attribute = item.attribute

            # Сейчас в detail нам нужно только одно значение на характеристику.
            # Если вдруг в базе случайно будет несколько значений одной характеристики,
            # берём первое и остальные игнорируем.
            if attribute.id in used_attribute_ids:
                continue

            value = ProductDetailService._get_attribute_value(item)

            if value is None:
                continue

            attributes.append({
                "id": attribute.id,
                "name": attribute.name,
                "slug": attribute.slug,
                "type": attribute.type,
                "value": value,
            })
            if attribute.unit:
                attributes[-1]["unit"] = attribute.unit

            used_attribute_ids.add(attribute.id)

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