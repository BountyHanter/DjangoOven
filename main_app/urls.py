from django.urls import path, include

from main_app.views.product_detail import ProductDetailAPIView
from main_app.views.product_preview import ProductCatalogAPIView
from main_app.views.review import ReviewListView
from main_app.views.section import CatalogFiltersAPIView

catalog_patterns = [
    path("filters/", CatalogFiltersAPIView.as_view(), name="catalog-filters"),
    path("products/", ProductCatalogAPIView.as_view(), name="catalog-products"),
    path("products/<int:id>/", ProductDetailAPIView.as_view(), name="catalog-product-detail"),
    path("reviews/", ReviewListView.as_view(), name="catalog-reviews"),
    path("products/<int:product_id>/reviews/", ReviewListView.as_view(), name="product-reviews"),
]

urlpatterns = [
    path("catalog/", include(catalog_patterns)),
]