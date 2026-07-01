import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from main_app.admin.forms.product import ProductAttributeValueInlineForm
from main_app.models import ProductAttribute, ProductAttributeOption


@pytest.fixture
def admin_user():
    return get_user_model().objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="password",
    )


@pytest.mark.django_db
def test_product_admin_attribute_meta_returns_options_for_selected_attribute(
    client,
    admin_user,
):
    client.force_login(admin_user)

    attribute = ProductAttribute.objects.create(
        name="Материал",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    other_attribute = ProductAttribute.objects.create(
        name="Топливо",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    steel = ProductAttributeOption.objects.create(
        attribute=attribute,
        value="Сталь",
    )
    soapstone = ProductAttributeOption.objects.create(
        attribute=attribute,
        value="Талькохлорит",
    )
    ProductAttributeOption.objects.create(
        attribute=other_attribute,
        value="Дрова",
    )

    response = client.get(
        reverse(
            "admin:main_app_product_attribute_meta",
            args=[attribute.id],
        )
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": attribute.id,
        "type": ProductAttribute.AttributeType.CHOICE,
        "options": [
            {
                "id": steel.id,
                "value": "Сталь",
            },
            {
                "id": soapstone.id,
                "value": "Талькохлорит",
            },
        ],
    }


@pytest.mark.django_db
def test_product_admin_attribute_meta_returns_empty_options_for_scalar_attribute(
    client,
    admin_user,
):
    client.force_login(admin_user)
    attribute = ProductAttribute.objects.create(
        name="Мощность",
        type=ProductAttribute.AttributeType.NUMBER,
    )

    response = client.get(
        reverse(
            "admin:main_app_product_attribute_meta",
            args=[attribute.id],
        )
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": attribute.id,
        "type": ProductAttribute.AttributeType.NUMBER,
        "options": [],
    }


@pytest.mark.django_db
def test_product_attribute_value_inline_form_filters_options_by_attribute():
    attribute = ProductAttribute.objects.create(
        name="Материал",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    other_attribute = ProductAttribute.objects.create(
        name="Топливо",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    steel = ProductAttributeOption.objects.create(
        attribute=attribute,
        value="Сталь",
    )
    ProductAttributeOption.objects.create(
        attribute=other_attribute,
        value="Дрова",
    )

    form = ProductAttributeValueInlineForm(
        prefix="attribute_values-0",
        data={
            "attribute_values-0-attribute": str(attribute.id),
        },
    )

    assert list(form.fields["option"].queryset) == [steel]
