from rest_framework import serializers


class EmailRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(min_length=5, max_length=20)
    link = serializers.CharField()

    def validate_phone(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Телефон пустой")
        return value

    def validate_link(self, value):
        value = value.strip()

        if not value.startswith("https://kamini-melnika.ru/"):
            raise serializers.ValidationError("Ссылка должна быть с kamini-melnika.ru")

        return value