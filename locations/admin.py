from django.contrib import admin
from locations.models import Building


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Building model.
    """

    list_display = ("title", "institution", "created_at")
    list_filter = ("institution",)
    search_fields = ("title", "institution__name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": (
                "title",
                "institution",
            )
        }),
    )
