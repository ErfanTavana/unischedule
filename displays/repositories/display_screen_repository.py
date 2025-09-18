from __future__ import annotations

from django.db.models import QuerySet

from displays.models import DisplayScreen


# --- Display screen operations -------------------------------------------------

def create_display_screen(data: dict) -> DisplayScreen:
    return DisplayScreen.objects.create(**data)


def list_display_screens(institution) -> QuerySet[DisplayScreen]:
    return (
        DisplayScreen.objects.filter(institution=institution, is_deleted=False)
        .select_related("institution")
        .order_by("title")
    )


def get_display_screen_by_id(screen_id: int, institution) -> DisplayScreen | None:
    return (
        DisplayScreen.objects.filter(
            id=screen_id,
            institution=institution,
            is_deleted=False,
        )
        .select_related("institution")
        .first()
    )


def get_display_screen_by_slug(slug: str, *, include_inactive: bool = False) -> DisplayScreen | None:
    qs = DisplayScreen.objects.filter(slug=slug, is_deleted=False).select_related("institution")
    if not include_inactive:
        qs = qs.filter(is_active=True)
    return qs.first()


def update_display_screen_fields(screen: DisplayScreen, fields: dict) -> DisplayScreen:
    for field, value in fields.items():
        setattr(screen, field, value)
    screen.save()
    return screen


def soft_delete_display_screen(screen: DisplayScreen) -> None:
    screen.delete()


