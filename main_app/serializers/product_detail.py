from rest_framework import serializers


class ProductDetailSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()

    manufacturer = serializers.DictField(allow_null=True)

    price = serializers.IntegerField()
    discount_price = serializers.IntegerField(allow_null=True)

    description = serializers.CharField(allow_null=True)
    schema = serializers.CharField(allow_null=True)

    free_delivery = serializers.BooleanField()
    in_stock = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_new = serializers.BooleanField()
    is_bestseller = serializers.BooleanField()
    priority = serializers.IntegerField(allow_null=True)
    sku = serializers.CharField(allow_blank=True)
    series = serializers.CharField(allow_blank=True)
    seo_title = serializers.CharField(allow_blank=True)
    seo_description = serializers.CharField(allow_blank=True)
    seo_keywords = serializers.CharField(allow_blank=True)

    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    sections = serializers.ListField()
    images = serializers.ListField()
    videos = serializers.ListField()
    documents = serializers.ListField()

    attributes = serializers.ListField()
