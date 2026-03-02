from main_app.models.choices import (
    PURPOSE_CHOICES,
    FUEL_TYPE_CHOICES,
    HEATED_VOLUME_CHOICES,
    STEAM_ROOM_VOLUME_CHOICES,
    POWER_KW_CHOICES,
    FIREBOX_MATERIAL_CHOICES,
    FIREBOX_TYPE_CHOICES,
    INSTALLATION_TYPE_CHOICES,
    FIREBOX_ORIENTATION_CHOICES,
    COMBUSTION_TYPE_CHOICES,
    GLASS_COUNT_CHOICES,
    FIRE_VIEW_CHOICES,
    CLADDING_MATERIAL_CHOICES,
    HEATER_TYPE_CHOICES,
    STONE_MATERIAL_CHOICES,
    TANK_TYPE_CHOICES,
    DOOR_MECHANISM_CHOICES,
    CHIMNEY_DIAMETER_CHOICES,
)

def build_choices_filter(choices):
    return [
        {
            "value": value,
            "label": label,
        }
        for value, label in choices
    ]

filters = {
    "purpose": build_choices_filter(PURPOSE_CHOICES),
    "fuel_type": build_choices_filter(FUEL_TYPE_CHOICES),
    "heated_volume": build_choices_filter(HEATED_VOLUME_CHOICES),
    "steam_room_volume": build_choices_filter(STEAM_ROOM_VOLUME_CHOICES),
    "power_kw": build_choices_filter(POWER_KW_CHOICES),

    "firebox_material": build_choices_filter(FIREBOX_MATERIAL_CHOICES),
    "firebox_type": build_choices_filter(FIREBOX_TYPE_CHOICES),
    "installation_type": build_choices_filter(INSTALLATION_TYPE_CHOICES),
    "firebox_orientation": build_choices_filter(FIREBOX_ORIENTATION_CHOICES),
    "combustion_type": build_choices_filter(COMBUSTION_TYPE_CHOICES),

    "glass_count": build_choices_filter(GLASS_COUNT_CHOICES),
    "fire_view": build_choices_filter(FIRE_VIEW_CHOICES),

    "cladding_material": build_choices_filter(CLADDING_MATERIAL_CHOICES),
    "heater_type": build_choices_filter(HEATER_TYPE_CHOICES),
    "stone_material": build_choices_filter(STONE_MATERIAL_CHOICES),
    "tank_type": build_choices_filter(TANK_TYPE_CHOICES),

    "door_mechanism": build_choices_filter(DOOR_MECHANISM_CHOICES),

    "chimney_diameter": build_choices_filter(CHIMNEY_DIAMETER_CHOICES),
}