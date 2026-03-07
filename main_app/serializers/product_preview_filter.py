from rest_framework import serializers
from main_app.models.choices import (
    HEATED_VOLUME_CHOICES,
    FIREBOX_MATERIAL_CHOICES,
    FIREBOX_TYPE_CHOICES,
    INSTALLATION_TYPE_CHOICES,
    GLASS_COUNT_CHOICES,
    FIRE_VIEW_CHOICES,
    HEATER_TYPE_CHOICES,
    STONE_MATERIAL_CHOICES,
    TANK_TYPE_CHOICES,
    DOOR_MECHANISM_CHOICES,
    CHIMNEY_CONNECTION_CHOICES,
    LINING_MATERIAL_CHOICES,
    FUEL_TYPE_CHOICES,
)


class ProductFilterSerializer(serializers.Serializer):

    search = serializers.CharField(required=False)

    section = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    manufacturer = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    # --- select ---
    fuel_type = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in FUEL_TYPE_CHOICES]
        ),
        required=False
    )

    heated_volume = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in HEATED_VOLUME_CHOICES]
        ),
        required=False
    )

    lining_material = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in LINING_MATERIAL_CHOICES]
        ),
        required=False
    )

    firebox_material = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in FIREBOX_MATERIAL_CHOICES]
        ),
        required=False
    )

    firebox_type = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in FIREBOX_TYPE_CHOICES]
        ),
        required=False
    )

    installation_type = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in INSTALLATION_TYPE_CHOICES]
        ),
        required=False
    )

    glass_count = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in GLASS_COUNT_CHOICES]
        ),
        required=False
    )

    fire_view = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in FIRE_VIEW_CHOICES]
        ),
        required=False
    )

    heater_type = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in HEATER_TYPE_CHOICES]
        ),
        required=False
    )

    stone_material = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in STONE_MATERIAL_CHOICES]
        ),
        required=False
    )

    tank_type = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in TANK_TYPE_CHOICES]
        ),
        required=False
    )

    door_mechanism = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in DOOR_MECHANISM_CHOICES]
        ),
        required=False
    )

    chimney_connection = serializers.ListField(
        child=serializers.ChoiceField(
            choices=[c[0] for c in CHIMNEY_CONNECTION_CHOICES]
        ),
        required=False
    )

    chimney_diameter = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    # --- boolean ---
    water_circuit = serializers.BooleanField(required=False)
    long_fire = serializers.BooleanField(required=False)
    heat_exchanger = serializers.BooleanField(required=False)
    glass_lift = serializers.BooleanField(required=False)
    damper = serializers.BooleanField(required=False)
    cooking_panel = serializers.BooleanField(required=False)

    # --- range ---
    price_from = serializers.IntegerField(required=False)
    price_to = serializers.IntegerField(required=False)

    power_kw_min = serializers.IntegerField(required=False)
    power_kw_max = serializers.IntegerField(required=False)

    steam_volume_from = serializers.IntegerField(required=False)
    steam_volume_to = serializers.IntegerField(required=False)

    ordering = serializers.CharField(required=False)