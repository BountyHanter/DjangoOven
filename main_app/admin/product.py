from django.contrib import admin
from django.utils.html import format_html

from main_app.admin.forms.product import ProductAdminForm, ProductDocumentInlineForm
from main_app.models.parser import ParserResult
from main_app.models.product import Product, ProductImage, ProductDocument

class ParserResultInline(admin.StackedInline):
    model = ParserResult
    extra = 1
    max_num = 1

    fields = (
        "url",
        "status",
        "processing_time",
        "error_text",
    )

    readonly_fields = (
        "status",
        "processing_time",
        "error_text",
    )

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image_preview", "image", "is_main", "ordering")
    readonly_fields = ("image_preview",)
    ordering = ("ordering",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px; max-width:120px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Превью"


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    form = ProductDocumentInlineForm
    extra = 1
    fields = ("title", "file", "ordering")
    ordering = ("ordering",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    inlines = [ParserResultInline, ProductImageInline, ProductDocumentInline]

    filter_horizontal = ("sections",)

    search_fields = (
        "name",
        "sku",
        "series",
    )

    list_display = (
        "name",
        "manufacturer",
        "fuel_type",
        "price",
        "discount_price",
        "in_stock",
        "is_active",
    )

    list_filter = (
        "manufacturer",
        "fuel_type",
        "heated_volume",
        "power_kw",
        "firebox_material",
        "firebox_type",
        "installation_type",
        "heater_type",
        "door_mechanism",
        "fire_view",
        "glass_count",
        "heat_exchanger",
        "glass_lift",
        "water_circuit",
        "damper",
        "cooking_panel",
        "free_delivery",
        "in_stock",
        "is_active",
        "is_new",
        "is_bestseller",
    )

    fieldsets = (

        (
            "Основная информация",
            {
                "fields": (
                    "name",
                    "manufacturer",
                    "sections",
                    "description",
                    "video_url",
                    "video_preview",
                    "schema",
                )
            },
        ),

        (
            "Цены",
            {
                "fields": (
                    "price",
                    "discount_price",
                )
            },
        ),

        (
            "Статусы",
            {
                "fields": (
                    "is_active",
                    "in_stock",
                    "free_delivery",
                    "is_new",
                    "is_bestseller",
                )
            },
        ),

        (
            "Параметры и характеристики",
            {
                "fields": (
                    "sku",
                    "series",
                    "fuel_type",
                    "heated_volume",
                    ("steam_volume_from", "steam_volume_to"),
                    "power_kw",
                    "lining_material",
                    "firebox_material",
                    "firebox_type",
                    "installation_type",
                    "heater_type",
                    "stone_material",
                    "tank_type",
                    "door_mechanism",
                    "fire_view",
                    "glass_count",
                    "chimney_diameter",
                    "chimney_connection",
                    "closed_heater_volume",
                    "warranty_years",
                    "efficiency",
                    "dimensions",
                    "weight",
                    "package_weight",
                    "stone_weight",
                    "long_fire",
                    "heat_exchanger",
                    "glass_lift",
                    "water_circuit",
                    "damper",
                    "cooking_panel",
                )
            },
        ),

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

        (
            "Загрузить множество изображений",
            {
                "fields": (
                    "images",
                )
            },
        ),

    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        images = form.cleaned_data.get("images") or []

        if not images:
            return

        start_order = obj.images.count()

        for i, image in enumerate(images, start=start_order):
            ProductImage.objects.create(
                product=obj,
                image=image,
                ordering=i,
            )

    class Media:
        js = ("admin/js/image_preview.js",)
        css = {
            "all": ("admin/css/image_preview.css",)
        }