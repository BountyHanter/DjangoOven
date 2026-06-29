from rest_framework import serializers


class ProductDetailSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()

    manufacturer = serializers.CharField(allow_null=True)

    price = serializers.IntegerField()
    discount_price = serializers.IntegerField(allow_null=True)

    description = serializers.CharField(allow_null=True)

    is_new = serializers.BooleanField()
    is_bestseller = serializers.BooleanField()
    priority = serializers.IntegerField(allow_null=True)

    created_at = serializers.DateTimeField()

    images = serializers.ListField()
    videos = serializers.ListField()
    documents = serializers.ListField()

    attributes = serializers.ListField()