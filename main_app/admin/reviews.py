from django.contrib import admin

from main_app.models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    # список в таблице
    list_display = (
        "name",
        "client_name",
        "product",
        "location",
        "price",
        "created_at",
    )

    # фильтры справа
    list_filter = (
        "product",
        "created_at",
    )

    # поиск
    search_fields = (
        "name",
        "client_name",
        "product__name",
        "location",
    )

    # порядок полей в форме
    fields = (
        "name",
        "client_name",
        "product",
        "location",
        "installation_time",
        "price",
        "video_url",
        "work_description",
        "created_at",
    )

    # readonly
    readonly_fields = (
        "created_at",
    )

    date_hierarchy = "created_at"