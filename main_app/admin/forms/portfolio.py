from django import forms

from main_app.admin.fields.product import MultipleImageField
from main_app.admin.forms.product import MultipleClearableFileInput
from main_app.models import Portfolio


class PortfolioAdminForm(forms.ModelForm):
    images = MultipleImageField(
        required=False,
        widget=MultipleClearableFileInput(attrs={"multiple": True}),
    )

    class Meta:
        model = Portfolio
        fields = "__all__"