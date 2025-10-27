from django.contrib import admin

from schedules.models.class_adjustment_model import ClassCancellation, MakeupClassSession
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


@admin.register(ClassCancellation)
class ClassCancellationAdmin(admin.ModelAdmin):
    list_display = (
        "institution",
        "class_session",
        "date",
        "reason",
        "is_deleted",
    )
    list_filter = (
        "institution",
        "class_session__course",
        "date",
        "is_deleted",
    )
    search_fields = (
        "class_session__course__title",
        "class_session__professor__last_name",
        "reason",
    )
    autocomplete_fields = ("institution", "class_session")
    ordering = ("-date",)


@admin.register(MakeupClassSession)
class MakeupClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        "institution",
        "class_session",
        "date",
        "start_time",
        "end_time",
        "classroom",
    )
    list_filter = (
        "institution",
        "class_session__course",
        "classroom",
        "date",
    )
    search_fields = (
        "class_session__course__title",
        "class_session__professor__last_name",
        "classroom__title",
        "group_code",
    )
    autocomplete_fields = ("institution", "class_session", "classroom")
    ordering = ("-date", "-start_time")
