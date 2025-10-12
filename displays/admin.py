from __future__ import annotations
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from displays.models import DisplayScreen


@admin.register(DisplayScreen)
class DisplayScreenAdmin(admin.ModelAdmin):
    # Display columns emphasise ownership, publication state, and quick access
    # to the public preview URL so operators can verify the feed at a glance.
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
    # Provide a one-click action that opens the unauthenticated JSON preview
    # used by kiosk devices.  Limited to single selection to avoid ambiguity.
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
        (
            "پیکربندی فیلتر",
            {
                "fields": (
                    "filter_title",
                    "filter_is_active",
                    "filter_classroom",
                    "filter_course",
                    "filter_professor",
                    "filter_semester",
                    "filter_day_of_week",
                    "filter_use_current_day_of_week",
                    "filter_week_type",
                    "filter_use_current_week_type",
                    "filter_date_override",
                    "filter_duration_seconds",
                    "filter_page_pause_seconds",
                )
            },
        ),
        ("شناسه‌ها", {
            "fields": ("slug", "access_token"),
            "classes": ("collapse",),
        }),
        ("زمان‌بندی", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="لینک JSON عمومی")
    def preview_link(self, obj: DisplayScreen) -> str:
        if obj is None or not getattr(obj, "pk", None) or not getattr(obj, "slug", None):
            return "Save to generate JSON URL"
        url = reverse("public-displays:public-display", args=[obj.slug])
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)

    @admin.display(description="آدرس JSON عمومی")
    def public_preview(self, obj: DisplayScreen) -> str:
        if obj is None or not getattr(obj, "slug", None):
            return "—"
        url = reverse("public-displays:public-display", args=[obj.slug])
        return format_html('<a href="{0}" target="_blank">{0}</a>', url)

    @admin.action(description="باز کردن JSON عمومی")
    def preview_screen(self, request, queryset):
        # Ensure that staff explicitly choose a single screen before
        # redirecting them to the external preview endpoint.
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
