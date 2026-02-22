from rest_framework import serializers
from main_app.models import Manufacturer


class ManufacturerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manufacturer
        fields = (
            "id",
            "name",
            "logo",
            "priority",
        )