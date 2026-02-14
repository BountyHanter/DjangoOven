from rest_framework import serializers


class ChoicesDisplayMixin(serializers.ModelSerializer):
    """
    Автоматически добавляет *_display
    для всех fields с choices.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)

        for field in instance._meta.fields:
            if field.choices:
                field_name = field.name
                display_method = f"get_{field_name}_display"

                if hasattr(instance, display_method):
                    data[f"{field_name}_display"] = getattr(
                        instance,
                        display_method
                    )()

        return data
