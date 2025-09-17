from __future__ import annotations

from typing import Iterable

from django.db.models import QuerySet

from displays.models import DisplayScreen, DisplayFilter, DisplayMessage


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


# --- Filter operations ---------------------------------------------------------

def create_display_filter(data: dict) -> DisplayFilter:
    return DisplayFilter.objects.create(**data)


def list_display_filters(screen: DisplayScreen) -> QuerySet[DisplayFilter]:
    return (
        screen.filters.filter(is_deleted=False)
        .select_related(
            "display_screen",
            "classroom__building__institution",
            "professor__institution",
            "course__institution",
            "semester__institution",
        )
        .order_by("position", "id")
    )


def get_display_filter_by_id(filter_id: int, institution) -> DisplayFilter | None:
    return (
        DisplayFilter.objects.filter(
            id=filter_id,
            display_screen__institution=institution,
            is_deleted=False,
        )
        .select_related(
            "display_screen__institution",
            "classroom__building__institution",
            "professor__institution",
            "course__institution",
            "semester__institution",
        )
        .first()
    )


def update_display_filter_fields(filter_obj: DisplayFilter, fields: dict) -> DisplayFilter:
    for field, value in fields.items():
        setattr(filter_obj, field, value)
    filter_obj.save()
    return filter_obj


def soft_delete_display_filter(filter_obj: DisplayFilter) -> None:
    filter_obj.delete()


# --- Messages ------------------------------------------------------------------

def list_active_messages(screen: DisplayScreen) -> Iterable[DisplayMessage]:
    return [msg for msg in screen.messages.filter(is_deleted=False) if msg.is_visible()]


def create_display_message(data: dict) -> DisplayMessage:
    return DisplayMessage.objects.create(**data)


def soft_delete_display_message(message: DisplayMessage) -> None:
    message.delete()
