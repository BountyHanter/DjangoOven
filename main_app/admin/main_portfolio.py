from django.contrib import admin

from main_app.models.main_portfolio import PortfolioImage, Portfolio


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):

    inlines = [PortfolioImageInline]

    list_display = (
        "title",
        "created_at",
    )

    search_fields = ("title",)
