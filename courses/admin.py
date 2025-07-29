from django.contrib import admin
from courses.models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Course model.
    """
    list_display = (
        "title",
        "code",
        "offer_code",
        "professor",
        "institution",
        "unit_count",
        "is_active",
    )
    list_filter = (
        "is_active",
        "unit_count",
        "professor",
        "institution",
    )
    search_fields = (
        "title",
        "code",
        "offer_code",
        "professor__first_name",
        "professor__last_name",
        "institution__name",
    )
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": (
                "title",
                "code",
                "offer_code",
                "professor",
                "institution",
                "unit_count",
                "is_active"
            )
        }),
    )
