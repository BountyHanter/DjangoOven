from django.contrib import admin
from django.utils.html import format_html

from main_app.models import Portfolio


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):

    # --- превью изображения ---
    def picture_preview(self, obj):
        if obj.picture and hasattr(obj.picture, "url"):
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;" />',
                obj.picture.url,
            )
        return "Нет изображения"

    picture_preview.short_description = "Превью"

    # --- список ---
    list_display = (
        "title",
        "product",
        "main",
        "price",
        "picture_preview",
        "created_at",
    )

    # --- readonly ---
    readonly_fields = (
        "picture_preview",
        "created_at",
    )

    # --- порядок полей в форме ---
    fields = (
        "title",
        "product",
        "main",
        "duration",
        "date",
        "object_type",
        "price",
        "video_link",
        "picture",
        "picture_preview",
        "type_work",
        "created_at",
    )

    list_filter = (
        "main",
        "product",
    )

    search_fields = (
        "title",
        "product__name",
    )