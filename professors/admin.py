from django.contrib import admin
from professors.models import Professor


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for the Professor model.
    """

    list_display = ("id", "first_name", "last_name", "national_code", "phone_number", "institution", "is_deleted", "created_at")
    list_filter = ("institution", "is_deleted", "created_at")
    search_fields = ("first_name", "last_name", "national_code", "phone_number")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {
            "fields": ("first_name", "last_name", "national_code", "phone_number", "institution")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
