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


from django.contrib import admin
from locations.models import Classroom

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Classroom model.
    """
    list_display = ("title", "building", "institution_display", "created_at")
    list_filter = ("building__title",)
    search_fields = ("title", "building__title")
    ordering = ("-created_at",)

    @admin.display(description="Institution")
    def institution_display(self, obj):
        return obj.building.institution.name  # ← اصلاح دقیق همین‌جاست ✅

    fieldsets = (
        (None, {
            "fields": ("title", "building")
        }),
    )
