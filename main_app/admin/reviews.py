from django.contrib import admin
from django.utils.html import format_html

from main_app.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    # --- превью картинки ---
    def preview_image_tag(self, obj):
        if obj.preview_image and hasattr(obj.preview_image, "url"):
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;" />',
                obj.preview_image.url,
            )
        return "Нет изображения"

    preview_image_tag.short_description = "Превью видео"

    # --- список ---
    list_display = (
        "client_name",
        "product",
        "location",
        "price",
        "preview_image_tag",
        "created_at",
    )

    list_select_related = ("product",)

    # --- readonly ---
    readonly_fields = (
        "preview_image_tag",
        "created_at",
    )

    # --- порядок полей ---
    fields = (
        "name",
        "client_name",
        "product",
        "installation_time",
        "location",
        "date",
        "work_description",
        "price",
        "video_url",
        "preview_image",
        "preview_image_tag",
        "created_at",
    )

    # --- фильтры ---
    list_filter = (
        "product",
        "created_at",
    )

    # --- поиск ---
    search_fields = (
        "client_name",
        "name",
        "product__name",
        "location",
    )

    ordering = ("-created_at",)

    class Media:
        js = ("admin/js/image_preview.js",)
        css = {
            "all": ("admin/css/image_preview.css",)
        }