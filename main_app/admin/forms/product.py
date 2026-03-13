from django import forms

from main_app.admin.fields.product import MultipleImageField
from main_app.models import Product, ProductDocument
from django.forms.widgets import ClearableFileInput

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