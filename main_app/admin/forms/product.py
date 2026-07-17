from django import forms
from django.db import models
from django.forms.widgets import ClearableFileInput

from main_app.admin.fields.product import MultipleImageField
from main_app.models import (
    Product,
    ProductAttributeOption,
    ProductAttributeValue,
    ProductDocument,
)


class MultipleClearableFileInput(ClearableFileInput):
    allow_multiple_selected = True


class ProductAdminForm(forms.ModelForm):
    images = MultipleImageField(
        required=False,
        widget=MultipleClearableFileInput(attrs={"multiple": True}),
        label="Загрузить изображения",
    )

    class Meta:
        model = Product
        fields = "__all__"


class ProductDocumentInlineForm(forms.ModelForm):
    class Meta:
        model = ProductDocument
        fields = "__all__"
        labels = {
            "title": "Документы (jpeg, png, webp)",
        }


class ProductAttributeValueInlineForm(forms.ModelForm):
    class Meta:
        model = ProductAttributeValue
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        attribute_id = self._get_attribute_id()

        if attribute_id:
            self.fields["option"].queryset = (
                ProductAttributeOption.objects
                .filter(attribute_id=attribute_id)
                .annotate(
                    priority_sort_group=models.Case(
                        models.When(priority=0, then=models.Value(1)),
                        default=models.Value(0),
                        output_field=models.IntegerField(),
                    )
                )
                .order_by("priority_sort_group", "priority", "id")
            )
            return

        self.fields["option"].queryset = ProductAttributeOption.objects.none()

    def _get_attribute_id(self):
        value = None

        if self.data:
            value = self.data.get(f"{self.prefix}-attribute")

        if not value and self.instance.pk:
            value = self.instance.attribute_id

        return self._normalize_id(value)

    @staticmethod
    def _normalize_id(value):
        if value in (None, ""):
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None
