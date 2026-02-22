from django.contrib import admin
from django.utils.html import format_html

from main_app.models import Manufacturer


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):

    def logo_preview(self, obj):
        if obj.logo and hasattr(obj.logo, "url"):
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;" />',
                obj.logo.url,
            )
        return "Нет изображения"

    logo_preview.short_description = "Превью логотипа"

    list_display = (
        "name",
        "is_active",
        "priority",
        "logo_preview",
        "created_at",
    )

    readonly_fields = (
        "logo_preview",
        "created_at",
        "updated_at",
    )

    fields = (
        "name",
        "is_active",
        "priority",
        "logo",
        "logo_preview",
        "created_at",
        "updated_at",
    )