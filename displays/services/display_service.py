from __future__ import annotations

from typing import Any, Iterable, List

from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError

from displays import repositories as display_repository
from displays.models import DisplayScreen
from displays.serializers import (
    DisplayScreenSerializer,
    DisplayScreenWriteSerializer,
    DisplayPublicPayloadSerializer,
)
from displays.utils import (
    compute_filter_day_of_week,
    compute_filter_week_type,
    parse_date,
    sort_filters,
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
    serializer = DisplayScreenWriteSerializer(data=data, context={"institution": institution})
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
    serializer = DisplayScreenWriteSerializer(
        instance=screen,
        data=data,
        partial=True,
        context={"institution": screen.institution},
    )
    _validate_serializer(serializer)
    updated = serializer.save()
    cache.delete(f"display:{updated.slug}")
    return DisplayScreenSerializer(updated).data


def delete_display_screen(screen: DisplayScreen) -> None:
    slug = screen.slug
    display_repository.soft_delete_display_screen(screen)
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


def _screen_filters(screen: DisplayScreen) -> list[dict[str, Any]]:
    if isinstance(screen.filters, list):
        return sort_filters(screen.filters)
    return []


def _active_screen_filters(screen: DisplayScreen) -> list[dict[str, Any]]:
    return [f for f in _screen_filters(screen) if f.get("is_active", True)]


def _query_sessions_for_filter(screen: DisplayScreen, filter_data: dict[str, Any]):
    qs = _base_session_queryset(screen)

    semester = filter_data.get("semester")
    if semester:
        qs = qs.filter(semester_id=semester)

    course = filter_data.get("course")
    if course:
        qs = qs.filter(course_id=course)

    professor = filter_data.get("professor")
    if professor:
        qs = qs.filter(professor_id=professor)

    classroom = filter_data.get("classroom")
    if classroom:
        qs = qs.filter(classroom_id=classroom)

    computed_day = compute_filter_day_of_week(filter_data)
    if computed_day:
        qs = qs.filter(day_of_week=computed_day)

    computed_week_type = compute_filter_week_type(filter_data)
    qs = _apply_week_type_filter(qs, computed_week_type)

    date_override = parse_date(filter_data.get("date_override"))
    if date_override:
        qs = qs.filter(
            semester__start_date__lte=date_override,
            semester__end_date__gte=date_override,
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
    filters = _active_screen_filters(screen)
    if not filters:
        return list(
            _base_session_queryset(screen).order_by("day_of_week", "start_time", "course__title")
        )

    collected: list[ClassSession] = []
    for filter_config in filters:
        collected.extend(list(_query_sessions_for_filter(screen, filter_config)))
    return _unique_sessions(collected)


def build_public_payload(screen: DisplayScreen, *, use_cache: bool = True) -> dict:
    cache_key = f"display:{screen.slug}"
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    sessions = _collect_sessions_for_screen(screen)
    sessions = _sort_sessions(sessions)

    filters = _active_screen_filters(screen)
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
