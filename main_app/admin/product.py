from django import forms
from django.contrib import admin
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path
from django.utils.html import format_html

from main_app.admin.forms.product import (
    ProductAdminForm,
    ProductAttributeValueInlineForm,
    ProductDocumentInlineForm,
)
from main_app.models.attribute import ProductAttribute, ProductAttributeValue
from main_app.models.parser import ParserResult
from main_app.models.product import Product, ProductImage, ProductDocument, ProductVideo


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


class ProductAttributeValueInline(admin.StackedInline):
    model = ProductAttributeValue
    form = ProductAttributeValueInlineForm
    extra = 1

    fields = (
        "attribute",
        "option",
        "value_number",
        "value_bool",
        "value_text",
    )

    autocomplete_fields = (
        "attribute",
    )

    formfield_overrides = {
        models.TextField: {
            "widget": forms.Textarea(attrs={
                "rows": 3,
                "cols": 40,
                "style": "width: 400px; resize: vertical;"
            })
        }
    }

    show_change_link = True

    class Media:
        js = ("admin/js/product_attribute_values.js",)
        css = {
            "all": ("admin/css/product_attribute_values.css",)
        }


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


class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1
    fields = ("url", "preview", "ordering")
    ordering = ("ordering",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm

    inlines = [
        ParserResultInline,
        ProductAttributeValueInline,
        ProductImageInline,
        ProductVideoInline,
        ProductDocumentInline,
    ]

    filter_horizontal = ("sections",)

    readonly_fields = ("id", "slug")

    search_fields = (
        "id",
        "name",
        "sku",
        "series",
        "manufacturer__name",
    )

    list_display = (
        "name",
        "manufacturer",
        "price",
        "discount_price",
        "in_stock",
        "is_active",
        "is_new",
        "is_bestseller",
    )

    list_filter = (
        "sections",
        "manufacturer",
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
                    "id",
                    "name",
                    "slug",
                    "manufacturer",
                    "sections",
                    "description",
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
            "Идентификаторы",
            {
                "fields": (
                    "priority",
                    "sku",
                    "series",
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "attribute-meta/<int:attribute_id>/",
                self.admin_site.admin_view(self.attribute_meta_view),
                name="main_app_product_attribute_meta",
            ),
        ]

        return custom_urls + urls

    def attribute_meta_view(self, request, attribute_id):
        attribute = get_object_or_404(ProductAttribute, pk=attribute_id)
        options = []

        if attribute.type == ProductAttribute.AttributeType.CHOICE:
            options = [
                {
                    "id": option.id,
                    "value": option.value,
                }
                for option in attribute.options.annotate(
                    priority_sort_group=models.Case(
                        models.When(priority=0, then=models.Value(1)),
                        default=models.Value(0),
                        output_field=models.IntegerField(),
                    )
                ).order_by("priority_sort_group", "priority", "id")
            ]

        return JsonResponse(
            {
                "id": attribute.id,
                "type": attribute.type,
                "options": options,
            }
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
