from django.contrib import admin
from django.utils.html import format_html

from main_app.models import Manufacturer, ManufacturerImage


class ManufacturerImageInline(admin.TabularInline):
    model = ManufacturerImage
    extra = 1

    # превью фото
    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, "url"):
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;" />',
                obj.image.url,
            )
        return "Нет изображения"

    image_preview.short_description = "Превью"

    readonly_fields = ("image_preview",)
    fields = ("image", "image_preview", "ordering")


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):

    inlines = [ManufacturerImageInline]

    # --- превью логотипа ---
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
        "slug",
        "is_active",
        "priority",

        "logo",
        "logo_preview",

        "keywords",
        "short_description",
        "description",
        "video",

        "created_at",
        "updated_at",
    )