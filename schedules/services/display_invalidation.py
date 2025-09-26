from __future__ import annotations

from typing import Iterable

from displays.models import DisplayScreen
from displays.repositories import display_screen_repository
from displays.services.display_service import invalidate_screen_cache
from displays.utils import compute_filter_day_of_week, compute_filter_week_type, parse_date
from schedules.models import ClassSession


def invalidate_related_displays(session: ClassSession, *, force: bool = False) -> None:
    """Invalidate cached payloads for displays that may reference ``session``.

    Parameters
    ----------
    session:
        The session instance that has been created, updated or deleted.
    force:
        When ``True`` the cache for all active screens of the institution is
        invalidated regardless of their filters. This is useful for scenarios
        where a session changes in a way that would make it fall outside a
        screen's filters (e.g. moving to another classroom).
    """

    if session is None or session.institution_id is None:
        return

    screens = display_screen_repository.list_active_display_screens_by_institution(
        session.institution
    )
    if not screens:
        return

    for screen in screens:
        if force or _session_might_affect_screen(screen, session):
            invalidate_screen_cache(screen)


def _session_might_affect_screen(screen: DisplayScreen, session: ClassSession) -> bool:
    if not screen.filter_is_active:
        return True

    selectors = _collect_selectors(screen)
    if not any(selectors):
        return True

    if screen.filter_classroom_id and screen.filter_classroom_id != session.classroom_id:
        return False

    if screen.filter_building_id:
        classroom = getattr(session, "classroom", None)
        building_id = getattr(classroom, "building_id", None) if classroom else None
        if building_id != screen.filter_building_id:
            return False

    if screen.filter_course_id and screen.filter_course_id != session.course_id:
        return False

    if screen.filter_professor_id and screen.filter_professor_id != session.professor_id:
        return False

    if screen.filter_semester_id and screen.filter_semester_id != session.semester_id:
        return False

    computed_day = compute_filter_day_of_week(screen)
    if computed_day and computed_day != session.day_of_week:
        return False

    computed_week_type = compute_filter_week_type(screen)
    if computed_week_type:
        if computed_week_type == ClassSession.WeekTypeChoices.EVERY:
            if session.week_type != ClassSession.WeekTypeChoices.EVERY:
                return False
        elif session.week_type not in (
            ClassSession.WeekTypeChoices.EVERY,
            computed_week_type,
        ):
            return False

    if screen.filter_group_code:
        group_code = session.group_code or ""
        if screen.filter_group_code != group_code:
            return False

    if screen.filter_start_time and session.start_time and session.start_time < screen.filter_start_time:
        return False

    if screen.filter_end_time and session.end_time and session.end_time > screen.filter_end_time:
        return False

    if screen.filter_capacity is not None:
        if session.capacity is None or session.capacity < screen.filter_capacity:
            return False

    date_override = parse_date(screen.filter_date_override)
    if date_override:
        semester = getattr(session, "semester", None)
        if not semester:
            return False
        if not (semester.start_date <= date_override <= semester.end_date):
            return False

    return True


def _collect_selectors(screen: DisplayScreen) -> Iterable[bool]:
    return (
        bool(screen.filter_classroom_id),
        bool(screen.filter_building_id),
        bool(screen.filter_course_id),
        bool(screen.filter_professor_id),
        bool(screen.filter_semester_id),
        bool(screen.filter_day_of_week),
        bool(screen.filter_week_type),
        bool(screen.filter_date_override),
        bool(screen.filter_group_code),
        bool(screen.filter_start_time),
        bool(screen.filter_end_time),
        screen.filter_capacity is not None,
    )
