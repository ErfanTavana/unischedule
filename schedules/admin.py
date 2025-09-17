from django.contrib import admin

from schedules.models.class_session_model import ClassSession


class ClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "professor",
        "classroom",
        "day_of_week",
        "start_time",
        "end_time",
        "week_type",
    )
    list_filter = ("institution", "semester", "day_of_week", "week_type")
    search_fields = ("course__title", "professor__last_name", "classroom__title")
    autocomplete_fields = ("course", "professor", "classroom", "semester")


admin.site.register(ClassSession, ClassSessionAdmin)
