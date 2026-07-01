from django.contrib import admin

from .product import ProductAdmin
from .reviews import ReviewAdmin
from .manufacturer import ManufacturerAdmin
from .portfolio import PortfolioAdmin
from .section import SectionAdmin
from .banner import BannerAdmin
from .attribute import *


_ATTRIBUTE_MODEL_NAMES = {
    "ProductAttribute",
    "ProductAttributeOption",
    "ProductAttributeValue",
}

_original_get_app_list = admin.site.get_app_list


def get_app_list_with_separate_attributes(request, app_label=None):
    app_list = _original_get_app_list(request, app_label)

    if app_label is not None:
        return app_list

    result = []

    for app in app_list:
        if app["app_label"] != "main_app":
            result.append(app)
            continue

        attribute_models = []
        other_models = []

        for model in app["models"]:
            if model["object_name"] in _ATTRIBUTE_MODEL_NAMES:
                attribute_models.append(model)
            else:
                other_models.append(model)

        if other_models:
            main_app = app.copy()
            main_app["models"] = other_models
            result.append(main_app)

        if attribute_models:
            attributes_app = app.copy()
            attributes_app["app_label"] = "main_app_attributes"
            attributes_app["app_url"] = ""
            attributes_app["name"] = "Характеристики"
            attributes_app["models"] = attribute_models
            result.append(attributes_app)

    return result


admin.site.get_app_list = get_app_list_with_separate_attributes
