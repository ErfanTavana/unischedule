from __future__ import annotations

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from displays.models import DisplayScreen, DisplayFilter, DisplayMessage


class DisplayFilterInline(admin.TabularInline):
    model = DisplayFilter
    extra = 0
    autocomplete_fields = ("classroom", "professor", "course", "semester")
    fields = (
        "title",
        "classroom",
        "professor",
        "course",
        "semester",
        "day_of_week",
        "week_type",
        "date_override",
        "position",
        "duration_seconds",
        "is_active",
    )


class DisplayMessageInline(admin.StackedInline):
    model = DisplayMessage
    extra = 0
    fields = ("content", "is_active", "priority", "starts_at", "ends_at")


@admin.register(DisplayScreen)
class DisplayScreenAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "institution",
        "slug",
        "layout_theme",
        "refresh_interval",
        "is_active",
        "updated_at",
        "public_preview",
    )
    list_filter = ("institution", "is_active", "layout_theme")
    search_fields = ("title", "slug", "institution__name")
    readonly_fields = ("slug", "access_token", "created_at", "updated_at", "preview_link")
    autocomplete_fields = ("institution",)
    inlines = [DisplayFilterInline, DisplayMessageInline]
    actions = ["preview_screen"]
    fieldsets = (
        (None, {
            "fields": (
                "institution",
                "title",
                "layout_theme",
                "refresh_interval",
                "is_active",
                "preview_link",
            )
        }),
        ("شناسه‌ها", {
            "fields": ("slug", "access_token"),
            "classes": ("collapse",),
        }),
        ("زمان‌بندی", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="لینک عمومی")
    def preview_link(self, obj: DisplayScreen) -> str:
        url = reverse("public-displays:public-display", args=[obj.slug])
        return format_html('<a href="{}" target="_blank">{}</a>', url, url)

    @admin.display(description="پیش‌نمایش")
    def public_preview(self, obj: DisplayScreen) -> str:
        url = reverse("public-displays:public-display", args=[obj.slug])
        return format_html('<a href="{}" target="_blank">نمایش</a>', url)

    @admin.action(description="پیش‌نمایش صفحه عمومی")
    def preview_screen(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "برای پیش‌نمایش تنها یک صفحه را انتخاب کنید.",
                level=messages.WARNING,
            )
            return None
        screen = queryset.first()
        url = reverse("public-displays:public-display", args=[screen.slug])
        return HttpResponseRedirect(url)


@admin.register(DisplayFilter)
class DisplayFilterAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "display_screen",
        "professor",
        "course",
        "classroom",
        "semester",
        "day_of_week",
        "week_type",
        "is_active",
    )
    list_filter = ("display_screen", "professor", "course", "classroom", "is_active")
    search_fields = ("title", "display_screen__title", "professor__last_name", "course__title")
    autocomplete_fields = ("display_screen", "classroom", "professor", "course", "semester")


@admin.register(DisplayMessage)
class DisplayMessageAdmin(admin.ModelAdmin):
    list_display = ("content", "display_screen", "priority", "is_active", "starts_at", "ends_at")
    list_filter = ("display_screen", "is_active")
    search_fields = ("content", "display_screen__title")
    autocomplete_fields = ("display_screen",)
