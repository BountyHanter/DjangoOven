from django.contrib import admin
from django.utils.html import format_html

from main_app.models.banner import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "manufacturer",
        "image_preview",
        "created_at",
    )

    list_filter = (
        "manufacturer",
        "sections",
    )

    search_fields = (
        "title",
    )

    filter_horizontal = (
        "sections",
    )

    readonly_fields = (
        "image_preview",
        "created_at",
        "updated_at",
    )

    fields = (
        "title",
        "manufacturer",
        "sections",
        "link",
        "image",
        "image_preview",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px;" />',
                obj.image.url
            )
        return "-"

    image_preview.short_description = "Превью"

    class Media:
        js = ("admin/js/image_preview.js",)
        css = {
            "all": ("admin/css/image_preview.css",)
        }