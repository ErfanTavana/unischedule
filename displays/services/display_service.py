from __future__ import annotations

from typing import Iterable, List

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
    """Apply the appropriate week-type filter for the current selector set.

    Screens can pin a specific week type (odd/even) but should also include
    sessions that are marked to occur every week.  This helper encapsulates
    that behaviour so it can be reused by both cached and uncached payload
    builders.
    """
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


def _sort_sessions(sessions: Iterable[ClassSession]) -> List[ClassSession]:
    return sorted(
        sessions,
        key=lambda session: (
            DAY_ORDER.get(session.day_of_week, 0),
            session.start_time,
            session.course.title,
        ),
    )


def _collect_sessions_for_screen(screen: DisplayScreen) -> List[ClassSession]:
    """Return all sessions that match the screen filter configuration.

    The function centralises the filtering logic so it can be reused when the
    payload is fetched from cache and when it is rebuilt.  It honours the
    activation flag, the user-provided selectors, and computed fallbacks such
    as day-of-week and week-type rules.
    """
    qs = _base_session_queryset(screen)

    if not screen.filter_is_active:
        return list(qs.order_by("day_of_week", "start_time", "course__title"))

    def _has_value(value) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return value.strip() != ""
        if isinstance(value, bool):
            return value
        return True

    selectors = [
        screen.filter_classroom_id,
        screen.filter_building_id,
        screen.filter_professor_id,
        screen.filter_course_id,
        screen.filter_semester_id,
        screen.filter_day_of_week,
        screen.filter_week_type,
        screen.filter_use_current_day_of_week,
        screen.filter_use_current_week_type,
        screen.filter_date_override,
        screen.filter_group_code,
        screen.filter_start_time,
        screen.filter_end_time,
        screen.filter_capacity,
    ]

    has_selector = any(_has_value(value) for value in selectors)

    if not has_selector:
        return list(qs.order_by("day_of_week", "start_time", "course__title"))

    if screen.filter_building_id:
        qs = qs.filter(classroom__building_id=screen.filter_building_id)

    if screen.filter_semester_id:
        qs = qs.filter(semester_id=screen.filter_semester_id)

    if screen.filter_course_id:
        qs = qs.filter(course_id=screen.filter_course_id)

    if screen.filter_professor_id:
        qs = qs.filter(professor_id=screen.filter_professor_id)

    if screen.filter_classroom_id:
        qs = qs.filter(classroom_id=screen.filter_classroom_id)

    if screen.filter_group_code:
        qs = qs.filter(group_code=screen.filter_group_code)

    if screen.filter_start_time:
        qs = qs.filter(start_time__gte=screen.filter_start_time)

    if screen.filter_end_time:
        qs = qs.filter(end_time__lte=screen.filter_end_time)

    if screen.filter_capacity is not None:
        qs = qs.filter(capacity__gte=screen.filter_capacity)

    computed_day = compute_filter_day_of_week(screen)
    if computed_day:
        qs = qs.filter(day_of_week=computed_day)

    computed_week_type = compute_filter_week_type(screen)
    qs = _apply_week_type_filter(qs, computed_week_type)

    date_override = parse_date(screen.filter_date_override)
    if date_override:
        qs = qs.filter(
            semester__start_date__lte=date_override,
            semester__end_date__gte=date_override,
        )

    return list(qs.order_by("day_of_week", "start_time", "course__title"))


def build_public_payload(screen: DisplayScreen, *, use_cache: bool = True) -> dict:
    """Serialize the public payload for a display screen.

    When ``use_cache`` is True a cached copy is returned if available, otherwise
    the session list is calculated, sorted and serialised together with the
    computed filter metadata.  Newly generated payloads are stored in the cache
    for the screen ``refresh_interval``.
    """
    # Cache keys are namespaced with the ``display:`` prefix so they do not
    # collide with other app caches; the slug uniquely identifies each screen.
    cache_key = f"display:{screen.slug}"
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    sessions = _collect_sessions_for_screen(screen)
    sessions = _sort_sessions(sessions)

    payload_serializer = DisplayPublicPayloadSerializer({
        "screen": screen,
        "filter": screen,
        "sessions": sessions,
        "generated_at": timezone.now(),
    })
    payload = payload_serializer.data

    if use_cache:
        cache.set(cache_key, payload, timeout=screen.refresh_interval)
    return payload


def invalidate_screen_cache(screen: DisplayScreen) -> None:
    """Remove the cached payload for the provided screen."""
    # Mirrors the naming strategy in ``build_public_payload`` to target only the
    # affected screen without disturbing other cached responses.
    cache.delete(f"display:{screen.slug}")
