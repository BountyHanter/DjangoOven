from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from main_app.serializers.email import EmailRequestSerializer
from main_app.utils.email_service import send_email


class SendEmailRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data["phone"]
        link = serializer.validated_data["link"]

        text_content = f"""
Новая заявка

Телефон: {phone}
Ссылка: {link}
"""

        html_content = f"""
<b>Новая заявка</b><br>
Телефон: {phone}<br>
Ссылка: {link}
"""

        send_email(
            subject="Новая заявка",
            to=settings.EMAIL_HOST_USER,
            text_content=text_content,
            html_content=html_content
        )

        return Response({"status": "ok"})