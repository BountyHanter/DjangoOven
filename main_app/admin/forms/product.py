from django import forms

from main_app.admin.fields.product import MultipleImageField
from main_app.models import Product
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