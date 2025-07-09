from django.contrib import admin
from semesters.models import Semester


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    """
    Admin panel for managing academic semesters.
    """

    list_display = ("title", "institution", "start_date", "end_date", "is_active", "created_at")
    list_filter = ("institution", "is_active", "start_date")
    search_fields = ("title",)
    ordering = ("-created_at",)
