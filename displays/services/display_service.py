from __future__ import annotations

from typing import Iterable, List

from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError

from displays import repositories as display_repository
from displays.models import DisplayScreen, DisplayFilter
from displays.serializers import (
    DisplayScreenSerializer,
    DisplayScreenWriteSerializer,
    DisplayFilterSerializer,
    DisplayFilterWriteSerializer,
    DisplayPublicPayloadSerializer,
)
from schedules.models import ClassSession

DAY_ORDER = {value: index for index, (value, _) in enumerate(ClassSession.DAY_OF_WEEK_CHOICES)}


def _ensure_institution(institution) -> None:
    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_REQUIRED["message"],
            code=ErrorCodes.INSTITUTION_REQUIRED["code"],
            status_code=ErrorCodes.INSTITUTION_REQUIRED["status_code"],
            errors=ErrorCodes.INSTITUTION_REQUIRED["errors"],
            data=ErrorCodes.INSTITUTION_REQUIRED["data"],
        )


def _validate_serializer(serializer) -> None:
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )


def list_display_screens(institution) -> list[dict]:
    _ensure_institution(institution)
    queryset = display_repository.list_display_screens(institution)
    return DisplayScreenSerializer(queryset, many=True).data


def create_display_screen(data: dict, institution) -> dict:
    _ensure_institution(institution)
    serializer = DisplayScreenWriteSerializer(data=data)
    _validate_serializer(serializer)
    screen = serializer.save(institution=institution)
    return DisplayScreenSerializer(screen).data


def get_display_screen_instance_or_404(screen_id: int, institution) -> DisplayScreen:
    _ensure_institution(institution)
    screen = display_repository.get_display_screen_by_id(screen_id, institution)
    if not screen:
        raise CustomValidationError(
            message=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["message"],
            code=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["code"],
            status_code=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["status_code"],
            errors=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["errors"],
        )
    return screen


def get_display_screen_by_id_or_404(screen_id: int, institution) -> dict:
    screen = get_display_screen_instance_or_404(screen_id, institution)
    return DisplayScreenSerializer(screen).data


def update_display_screen(screen: DisplayScreen, data: dict) -> dict:
    serializer = DisplayScreenWriteSerializer(instance=screen, data=data, partial=True)
    _validate_serializer(serializer)
    updated = serializer.save()
    cache.delete(f"display:{updated.slug}")
    return DisplayScreenSerializer(updated).data


def delete_display_screen(screen: DisplayScreen) -> None:
    slug = screen.slug
    display_repository.soft_delete_display_screen(screen)
    cache.delete(f"display:{slug}")


def list_display_filters(screen: DisplayScreen) -> list[dict]:
    filters = display_repository.list_display_filters(screen)
    return DisplayFilterSerializer(filters, many=True).data


def create_display_filter(screen: DisplayScreen, data: dict) -> dict:
    context = {"display_screen": screen, "institution": screen.institution}
    serializer = DisplayFilterWriteSerializer(data=data, context=context)
    _validate_serializer(serializer)
    filter_obj = serializer.save(display_screen=screen)
    cache.delete(f"display:{screen.slug}")
    return DisplayFilterSerializer(filter_obj).data


def get_display_filter_instance_or_404(filter_id: int, institution) -> DisplayFilter:
    _ensure_institution(institution)
    filter_obj = display_repository.get_display_filter_by_id(filter_id, institution)
    if not filter_obj:
        raise CustomValidationError(
            message=ErrorCodes.DISPLAY_FILTER_NOT_FOUND["message"],
            code=ErrorCodes.DISPLAY_FILTER_NOT_FOUND["code"],
            status_code=ErrorCodes.DISPLAY_FILTER_NOT_FOUND["status_code"],
            errors=ErrorCodes.DISPLAY_FILTER_NOT_FOUND["errors"],
        )
    return filter_obj


def update_display_filter(filter_obj: DisplayFilter, data: dict) -> dict:
    context = {
        "display_screen": filter_obj.display_screen,
        "institution": filter_obj.display_screen.institution,
    }
    serializer = DisplayFilterWriteSerializer(
        instance=filter_obj,
        data=data,
        partial=True,
        context=context,
    )
    _validate_serializer(serializer)
    updated = serializer.save()
    cache.delete(f"display:{filter_obj.display_screen.slug}")
    return DisplayFilterSerializer(updated).data


def delete_display_filter(filter_obj: DisplayFilter) -> None:
    slug = filter_obj.display_screen.slug
    display_repository.soft_delete_display_filter(filter_obj)
    cache.delete(f"display:{slug}")


def get_display_screen_by_slug_or_404(slug: str) -> DisplayScreen:
    screen = display_repository.get_display_screen_by_slug(slug)
    if not screen:
        raise CustomValidationError(
            message=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["message"],
            code=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["code"],
            status_code=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["status_code"],
            errors=ErrorCodes.DISPLAY_SCREEN_NOT_FOUND["errors"],
        )
    return screen


def _apply_week_type_filter(qs, week_type: str | None):
    if not week_type:
        return qs
    if week_type == ClassSession.WeekTypeChoices.EVERY:
        return qs.filter(week_type=ClassSession.WeekTypeChoices.EVERY)
    return qs.filter(
        Q(week_type=week_type) | Q(week_type=ClassSession.WeekTypeChoices.EVERY)
    )


def _base_session_queryset(screen: DisplayScreen):
    return (
        ClassSession.objects.filter(
            institution=screen.institution,
            is_deleted=False,
        )
        .select_related("course", "professor", "classroom__building", "semester")
    )


def _query_sessions_for_filter(filter_obj: DisplayFilter):
    qs = _base_session_queryset(filter_obj.display_screen)
    if filter_obj.semester:
        qs = qs.filter(semester=filter_obj.semester)
    if filter_obj.course:
        qs = qs.filter(course=filter_obj.course)
    if filter_obj.professor:
        qs = qs.filter(professor=filter_obj.professor)
    if filter_obj.classroom:
        qs = qs.filter(classroom=filter_obj.classroom)

    computed_day = filter_obj.computed_day_of_week
    if computed_day:
        qs = qs.filter(day_of_week=computed_day)

    qs = _apply_week_type_filter(qs, filter_obj.computed_week_type)

    if filter_obj.date_override:
        qs = qs.filter(
            semester__start_date__lte=filter_obj.date_override,
            semester__end_date__gte=filter_obj.date_override,
        )

    return qs.order_by("day_of_week", "start_time", "course__title")


def _sort_sessions(sessions: Iterable[ClassSession]) -> List[ClassSession]:
    return sorted(
        sessions,
        key=lambda session: (
            DAY_ORDER.get(session.day_of_week, 0),
            session.start_time,
            session.course.title,
        ),
    )


def _unique_sessions(sessions: Iterable[ClassSession]) -> List[ClassSession]:
    unique: dict[int, ClassSession] = {}
    for session in sessions:
        unique[session.id] = session
    return list(unique.values())


def _collect_sessions_for_screen(screen: DisplayScreen) -> List[ClassSession]:
    filters = [f for f in display_repository.list_display_filters(screen) if f.is_active]
    if not filters:
        return list(
            _base_session_queryset(screen).order_by("day_of_week", "start_time", "course__title")
        )

    collected: list[ClassSession] = []
    for filter_obj in filters:
        collected.extend(list(_query_sessions_for_filter(filter_obj)))
    return _unique_sessions(collected)


def build_public_payload(screen: DisplayScreen, *, use_cache: bool = True) -> dict:
    cache_key = f"display:{screen.slug}"
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    sessions = _collect_sessions_for_screen(screen)
    sessions = _sort_sessions(sessions)

    filters = [f for f in display_repository.list_display_filters(screen) if f.is_active]
    messages = list(display_repository.list_active_messages(screen))

    payload_serializer = DisplayPublicPayloadSerializer({
        "screen": screen,
        "filters": filters,
        "sessions": sessions,
        "messages": messages,
        "generated_at": timezone.now(),
    })
    payload = payload_serializer.data

    if use_cache:
        cache.set(cache_key, payload, timeout=screen.refresh_interval)
    return payload


def invalidate_screen_cache(screen: DisplayScreen) -> None:
    cache.delete(f"display:{screen.slug}")
