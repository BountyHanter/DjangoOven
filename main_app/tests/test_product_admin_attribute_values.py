import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from main_app.admin.forms.product import ProductAttributeValueInlineForm
from main_app.models import Product, ProductAttribute, ProductAttributeOption


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
def test_product_admin_attribute_meta_returns_range_type(
    client,
    admin_user,
):
    client.force_login(admin_user)
    attribute = ProductAttribute.objects.create(
        name="Объем отопления",
        type=ProductAttribute.AttributeType.RANGE,
        unit="м3",
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
        "type": ProductAttribute.AttributeType.RANGE,
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


@pytest.mark.django_db(transaction=True)
def test_product_admin_loads_options_in_dynamically_added_attribute_row(
    live_server,
    admin_user,
    settings,
):
    settings.SESSION_COOKIE_SECURE = False
    settings.CSRF_COOKIE_SECURE = False

    product = Product.objects.create(
        name="Тестовая печь",
        price=100_000,
    )
    attribute = ProductAttribute.objects.create(
        name="Материал",
        type=ProductAttribute.AttributeType.CHOICE,
    )
    steel = ProductAttributeOption.objects.create(
        attribute=attribute,
        value="Сталь",
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()

        login_url = f"{live_server.url}{reverse('admin:login')}"
        page.goto(login_url)
        page.get_by_label("Имя пользователя:").fill(admin_user.username)
        page.get_by_label("Пароль:").fill("password")
        page.get_by_role("button", name="Войти").click()

        change_path = reverse(
            "admin:main_app_product_change",
            args=[product.pk],
        )
        change_url = f"{live_server.url}{change_path}"
        page.goto(change_url)

        empty_form = page.locator("#attribute_values-empty")
        expect(empty_form).not_to_have_attribute(
            "data-product-attribute-values-initialized",
            "true",
        )

        page.locator("#attribute_values-group .add-row a").click()
        added_row = page.locator("#attribute_values-1")
        expect(added_row).to_be_visible()

        attribute_select = added_row.locator(".field-attribute select")
        attribute_select.evaluate(
            """
            (select, attribute) => {
                const option = document.createElement("option");
                option.value = String(attribute.id);
                option.textContent = attribute.name;
                option.selected = true;
                select.appendChild(option);
                select.dispatchEvent(new Event("change", {bubbles: true}));
            }
            """,
            {"id": attribute.pk, "name": attribute.name},
        )

        option_field = added_row.locator(".field-option")
        expect(option_field).to_be_visible()
        expect(option_field.locator("select")).to_have_value("")
        expect(option_field.locator(f"option[value='{steel.pk}']")).to_have_text(
            steel.value
        )

        browser.close()
