from django.contrib import admin
from main_app.models.review import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "client_name",
        "location",
        "price",
        "created_at",
    )

    search_fields = (
        "client_name",
        "location",
        "work_description",
    )

    list_filter = ("created_at",)

    fieldsets = (
        (
            "Основная информация",
            {
                "fields": (
                    "client_name",
                    "location",
                    "price",
                )
            },
        ),
        (
            "Детали работ",
            {
                "fields": (
                    "installation_time",
                    "work_description",
                    "video_url",
                )
            },
        ),
    )
