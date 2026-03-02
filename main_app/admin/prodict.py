from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from django.utils.html import format_html

from main_app.admin.forms.product import ProductAdminForm
from main_app.models.product import Product, ProductImage, ProductDocument
from main_app.models.section import Section

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
                '<img src="{}" style="max-height:120px; max-width:120px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "Превью"

class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1
    fields = ("title", "file", "ordering")
    ordering = ("ordering",)


def _has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except FieldDoesNotExist:
        return False


def _filter_fields(model, fields):
    """
    Поля могут быть:
      - "field"
      - ("field1", "field2")
    Возвращаем только существующие.
    """
    out = []

    for item in fields:
        if isinstance(item, (tuple, list)):
            exists = [f for f in item if _has_field(model, f)]

            if len(exists) >= 2:
                out.append(tuple(exists))
            elif len(exists) == 1:
                out.append(exists[0])
        else:
            if _has_field(model, item):
                out.append(item)

    return tuple(out)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    # inline остаются — для редактирования
    inlines = [ProductImageInline, ProductDocumentInline]

    filter_horizontal = ("sections",)
    search_fields = ("name", "sku", "series")
    list_select_related = ("manufacturer",)

    def get_list_display(self, request):
        base = (
            "name",
            "manufacturer",
            "purpose",
            "fuel_type",
            "price",
            "discount_price",
            "in_stock",
            "is_active",
        )
        return _filter_fields(Product, base)

    def get_list_filter(self, request):
        base = (
            "manufacturer",
            "purpose",
            "fuel_type",
            "heated_volume",
            "steam_room_volume",
            "power_kw",
            "firebox_material",
            "firebox_type",
            "installation_type",
            "firebox_orientation",
            "combustion_type",
            "cladding_material",
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
            "is_popular",
            "is_discount",
            "is_new",
            "is_bestseller",
        )
        return _filter_fields(Product, base)

    def get_fieldsets(self, request, obj=None):
        fs = (
            (
                "Основная информация",
                {
                    "fields": _filter_fields(
                        Product,
                        (
                            "name",
                            "manufacturer",
                            "sections",
                            "description",
                            "video_url",
                            "images",
                        ),
                    )
                },
            ),
            (
                "Цены",
                {
                    "fields": _filter_fields(
                        Product,
                        ("price", "discount_price", "price_in_euro"),
                    )
                },
            ),
            (
                "Статусы",
                {
                    "fields": _filter_fields(
                        Product,
                        (
                            "is_active",
                            "in_stock",
                            "free_delivery",
                            "is_popular",
                            "is_new",
                            "is_bestseller",
                        ),
                    )
                },
            ),
            (
                "Параметры и характеристики",
                {
                    "fields": _filter_fields(
                        Product,
                        (
                            "sku",
                            "series",
                            "purpose",
                            "fuel_type",
                            "heated_volume",
                            "steam_room_volume",
                            ("steam_volume_from", "steam_volume_to"),
                            "power_kw",
                            "firebox_material",
                            "firebox_type",
                            "installation_type",
                            "firebox_orientation",
                            "combustion_type",
                            "cladding_material",
                            "heater_type",
                            "stone_material",
                            "tank_type",
                            "door_type",
                            "door_mechanism",
                            "fire_view",
                            "glass_count",
                            "chimney_diameter",
                            "dimensions",
                            "weight",
                            "stone_weight",
                            "heat_exchanger",
                            "glass_lift",
                            "water_circuit",
                            "damper",
                            "cooking_panel",
                        ),
                    )
                },
            ),
            (
                "SEO",
                {
                    "fields": _filter_fields(
                        Product,
                        ("seo_title", "seo_description", "seo_keywords"),
                    )
                },
            ),
        )
        return fs

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # берём файлы из формы (правильный способ)
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