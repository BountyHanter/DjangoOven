from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from slugify import slugify

from main_app.models.attribute import (
    ProductAttribute,
    ProductAttributeOption,
    ProductAttributeValue,
)


class ProductAttributeOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        used_slugs = set()

        # Если редактируем уже существующую характеристику,
        # учитываем уже сохранённые варианты.
        if self.instance.pk:
            current_form_pks = []

            for form in self.forms:
                if form.instance.pk:
                    current_form_pks.append(form.instance.pk)

            existing_slugs = ProductAttributeOption.objects.filter(
                attribute=self.instance,
            ).exclude(
                pk__in=current_form_pks,
            ).values_list(
                "slug",
                flat=True,
            )

            used_slugs.update(existing_slugs)

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue

            cleaned_data = form.cleaned_data

            if not cleaned_data:
                continue

            if cleaned_data.get("DELETE"):
                continue

            value = cleaned_data.get("value")
            slug = cleaned_data.get("slug")

            if not value:
                continue

            if not slug:
                base_slug = slugify(value) or "option"
                slug = base_slug
                counter = 1

                while slug in used_slugs:
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                cleaned_data["slug"] = slug
                form.instance.slug = slug

            used_slugs.add(slug)

        super().clean()


class ProductAttributeOptionInline(admin.TabularInline):
    model = ProductAttributeOption
    formset = ProductAttributeOptionInlineFormSet
    extra = 1

    fields = (
        "value",
        "slug",
        "is_active",
    )

    readonly_fields = (
        "slug",
    )

    show_change_link = True


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "type",
        "allow_multiple",
        "unit",
        "options_count",
    )

    list_filter = (
        "type",
        "allow_multiple",
    )

    search_fields = (
        "name",
        "slug",
    )

    readonly_fields = (
        "slug",
    )

    inlines = [
        ProductAttributeOptionInline,
    ]

    def options_count(self, obj):
        return obj.options.count()

    options_count.short_description = "Кол-во вариантов"


@admin.register(ProductAttributeOption)
class ProductAttributeOptionAdmin(admin.ModelAdmin):
    list_display = (
        "value",
        "attribute",
        "slug",
        "is_active",
    )

    list_filter = (
        "attribute",
        "is_active",
    )

    search_fields = (
        "value",
        "slug",
        "attribute__name",
    )

    autocomplete_fields = (
        "attribute",
    )

    readonly_fields = (
        "slug",
    )


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "attribute",
        "display_value",
        "option",
        "value_number",
        "value_bool",
    )

    list_filter = (
        "attribute",
        "attribute__type",
    )

    search_fields = (
        "product__name",
        "attribute__name",
        "option__value",
        "value_text",
    )

    autocomplete_fields = (
        "product",
        "attribute",
        "option",
    )

    readonly_fields = (
        "display_value",
        "created_at",
        "updated_at",
    )
