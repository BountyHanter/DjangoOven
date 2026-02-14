from django.contrib import admin

from main_app.models import CatalogPortfolioHistory, CatalogPortfolioImage, CatalogPortfolio, \
    CatalogPortfolioProductImage


class CatalogPortfolioHistoryInline(admin.TabularInline):
    model = CatalogPortfolioHistory
    extra = 1
    fields = ("text", "ordering")
    ordering = ("ordering",)

class CatalogPortfolioImageInline(admin.TabularInline):
    model = CatalogPortfolioImage
    extra = 1

class CatalogPortfolioProductInline(admin.TabularInline):
    model = CatalogPortfolioProductImage
    extra = 1

@admin.register(CatalogPortfolio)
class CatalogPortfolioAdmin(admin.ModelAdmin):

    inlines = [
        CatalogPortfolioImageInline,
        CatalogPortfolioProductInline,
        CatalogPortfolioHistoryInline,
    ]

    list_display = (
        "title",
        "catalog_type",
        "project_price",
        "is_active",
        "created_at",
    )

    list_filter = (
        "catalog_type",
        "is_active",
    )

    search_fields = (
        "title",
        "client_problem",
    )

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "title",
                    "client_problem",
                    "catalog_type",
                )
            },
        ),
        (
            "Проект",
            {
                "fields": (
                    "project_price",
                    "production_time",
                    "production_date",
                    "object_type",
                    "work_types",
                    "video_url",
                )
            },
        ),
        (
            "Статус",
            {
                "fields": ("is_active",)
            },
        ),
    )
