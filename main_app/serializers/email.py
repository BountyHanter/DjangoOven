import logging
from urllib.parse import urlparse

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

        parsed = urlparse(value)

        allowed_hosts = {
            "kamini-melnika.ru",
            "www.kamini-melnika.ru",
        }

        if parsed.hostname not in allowed_hosts:
            logger.warning(
                "Ошибка отправки email. Не верная ссылка: %s",
                value,
            )
            raise serializers.ValidationError(
                "Ссылка должна быть с kamini-melnika.ru"
            )

        return value