from django.contrib import admin
from django.utils.html import format_html

from main_app.models.manufacturer import Manufacturer
from main_app.models.product import ProductImage, ProductDocument, Product
from main_app.models.section import Section

admin.site.register(Manufacturer)
admin.site.register(Section)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image_preview", "image", "is_main", "ordering")
    readonly_fields = ("image_preview",)
    ordering = ("ordering",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 120px; max-width: 120px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Превью"

class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1
    fields = ("title", "file", "ordering")
    ordering = ("ordering",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductDocumentInline]

    list_display = (
        "name",
        "manufacturer",
        "price",
        "discount_price",
        "in_stock",
        "is_active",
    )

    list_filter = (
        "manufacturer",
        "fuel_type",
        "placement",
        "facing_type",
        "in_stock",
        "is_active",
        "free_delivery",
    )

    search_fields = (
        "name",
        "sku",
        "series",
    )

    filter_horizontal = ("sections",)

    fieldsets = (
        # --- ОСНОВНАЯ ИНФОРМАЦИЯ ---
        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "manufacturer",
                    "sections",
                    "description",
                    "video_url",
                )
            },
        ),

        # --- ЦЕНЫ ---
        (
            "Цены",
            {
                "fields": (
                    "price",
                    "discount_price",
                    "price_in_euro",
                )
            },
        ),

        # --- СТАТУСЫ ---
        (
            "Статусы",
            {
                "fields": (
                    "is_active",
                    "in_stock",
                    "free_delivery",
                    "is_popular",
                )
            },
        ),

        # --- ПАРАМЕТРЫ И ХАРАКТЕРИСТИКИ ---
        (
            "Параметры и характеристики",
            {
                "fields": (
                    "sku",
                    "series",
                    "dimensions",
                    "weight",
                    "heated_volume",
                    ("steam_volume_from", "steam_volume_to"),
                    "chimney_diameter",
                    "power_kw",
                    "stone_weight",
                    "material",
                    "firebox_material",
                    "stone_material",
                    "door_type",
                    "door_mechanism",
                    "fire_view",
                    "glass_count",
                    "fuel_type",
                    "tank_type",
                    "firebox_type",
                    "stone_type",
                    "water_heating",
                    "placement",
                    "facing_type",
                    "heat_exchanger",
                    "long_burning",
                    "glass_lift",
                    "damper",
                    "cooking_panel",
                )
            },
        ),

        # --- SEO ---
        (
            "SEO",
            {
                "fields": (
                    "seo_title",
                    "seo_description",
                    "seo_keywords",
                )
            },
        ),
    )
