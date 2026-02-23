from django.urls import path, include

from main_app.views.manufacturer import ManufacturerPreviewListView, ManufacturerDetailAPIView
from main_app.views.portfolio import PortfolioListAPIView
from main_app.views.product_detail import ProductDetailAPIView
from main_app.views.product_preview import ProductCatalogAPIView
from main_app.views.review import ReviewListView
from main_app.views.section import CatalogFiltersAPIView

catalog_patterns = [
    path("filters/", CatalogFiltersAPIView.as_view(), name="catalog-filters"),

    # продукты
    path("products/", ProductCatalogAPIView.as_view(), name="catalog-products"),
    path("products/<int:id>/", ProductDetailAPIView.as_view(), name="catalog-product-detail"),

    # портфолио
    path("portfolio/", PortfolioListAPIView.as_view(), name="catalog-portfolio"),
    path( "products/<int:product_id>/portfolio/", PortfolioListAPIView.as_view(), name="product-portfolio"),

    # отзывы
    path("reviews/", ReviewListView.as_view(), name="catalog-reviews"),
    path("products/<int:product_id>/reviews/", ReviewListView.as_view(), name="product-reviews"),

    # бренды
    path("manufacturers/", ManufacturerPreviewListView.as_view(), name="catalog-manufacturers"),
    path("manufacturers/<int:id>/", ManufacturerDetailAPIView.as_view(), name="catalog-manufacturer-detail"),
]

urlpatterns = [
    path("catalog/", include(catalog_patterns)),
]