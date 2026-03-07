from django.contrib import admin
from django.utils.html import format_html

from main_app.models import Portfolio, PortfolioImage

class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    fields = ("image", "order", "image_preview")
    readonly_fields = ("image_preview",)
    ordering = ("order", "id")

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, "url"):
            return format_html(
                '<img src="{}" style="max-height:100px;border-radius:6px;" />',
                obj.image.url,
            )
        return "Нет изображения"

    image_preview.short_description = "Превью"

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):

    # ----- inline галерея -----
    inlines = [PortfolioImageInline]

    # ----- превью обложки (первая фотка) -----
    def preview(self, obj):
        image = obj.images.first()
        if image and image.image:
            return format_html(
                '<img src="{}" style="max-height:120px;border-radius:6px;" />',
                image.image.url,
            )
        return "Нет изображения"

    preview.short_description = "Превью"

    # ----- список -----
    list_display = (
        "title",
        "product",
        "main",
        "price",
        "preview",
        "created_at",
    )

    list_display_links = ("title",)

    # ----- readonly -----
    readonly_fields = (
        "preview",
        "created_at",
    )

    # ----- порядок полей формы -----
    fields = (
        "title",
        "product",
        "main",
        "duration",
        "date",
        "object_type",
        "price",
        "video_link",
        "preview",
        "type_work",
        "created_at",
    )

    # ----- фильтры -----
    list_filter = (
        "main",
        "product",
        "created_at",
    )

    # ----- поиск -----
    search_fields = (
        "title",
        "product__name",
    )

    # ----- сортировка -----
    ordering = ("-created_at",)

    # ----- оптимизация запросов -----
    list_select_related = ("product",)

    class Media:
        js = ("admin/js/image_preview.js",)
        css = {
            "all": ("admin/css/image_preview.css",)
        }