from django.contrib import admin
from django.utils.html import format_html

from main_app.models.section import Section


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "image_preview",
        "parent",
        "ordering",
        "is_active",
    )

    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug", "menu_name")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("parent__id", "ordering", "name")

    fields = (
        "name",
        "slug",
        "parent",
        "description_main",
        "image",
        "image_preview",
        "menu_name",
        "browser_title",
        "description",
        "meta_description",
        "meta_keywords",
        "ordering",
        "is_active",
    )

    readonly_fields = ("image_preview",)

    # ✅ превью картинки
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px; max-width:120px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Превью"

    class Media:
        js = ("admin/js/image_preview.js",)
        css = {
            "all": ("admin/css/image_preview.css",)
        }