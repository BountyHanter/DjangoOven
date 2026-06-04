import logging

from rest_framework import serializers

logger = logging.getLogger(__name__)

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
            logger.warning(f"Ошибка отправки email. Не верная ссылка: {value}")
            raise serializers.ValidationError("Ссылка должна быть с kamini-melnika.ru")

        return value