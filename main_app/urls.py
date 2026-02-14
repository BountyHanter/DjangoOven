from django.urls import path

from main_app.views.product_detail import ProductDetailAPIView
from main_app.views.product_preview import ProductCatalogAPIView
from main_app.views.section import CatalogFiltersAPIView

urlpatterns = [
    path("catalog/filters/", CatalogFiltersAPIView.as_view(), name="catalog-filters"),
    path("catalog/products/", ProductCatalogAPIView.as_view(), name="catalog-products"),
    path("catalog/products/<int:id>/", ProductDetailAPIView.as_view(), name="catalog-product-detail"),

]