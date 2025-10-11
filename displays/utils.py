from __future__ import annotations

from datetime import date
from typing import Any

from django.utils import timezone

from schedules.models import ClassSession

from displays.models.display_models import PY_WEEKDAY_TO_PERSIAN
from semesters.models import Semester
from semesters.repositories import semester_repository


def parse_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _get_value(filter_data: Any, key: str) -> Any:
    if isinstance(filter_data, dict):
        return filter_data.get(key)
    return getattr(filter_data, key, None)


def compute_filter_day_of_week(filter_data: Any) -> str | None:
    day = _get_value(filter_data, "day_of_week") or _get_value(filter_data, "filter_day_of_week")
    if day:
        return day
    override = parse_date(
        _get_value(filter_data, "date_override")
        or _get_value(filter_data, "filter_date_override")
    )
    if override:
        return PY_WEEKDAY_TO_PERSIAN.get(override.weekday())
    use_current = _get_value(filter_data, "use_current_day_of_week") or _get_value(
        filter_data, "filter_use_current_day_of_week"
    )
    if use_current:
        today = timezone.localdate()
        return PY_WEEKDAY_TO_PERSIAN.get(today.weekday())
    return None


def compute_filter_week_type(filter_data: Any) -> str | None:
    week_type = _get_value(filter_data, "week_type") or _get_value(
        filter_data, "filter_week_type"
    )
    if week_type:
        return week_type
    use_current = _get_value(filter_data, "use_current_week_type") or _get_value(
        filter_data, "filter_use_current_week_type"
    )
    if not use_current:
        return None

    reference_date = parse_date(
        _get_value(filter_data, "date_override")
        or _get_value(filter_data, "filter_date_override")
    )
    if reference_date is None:
        reference_date = timezone.localdate()

    semester = _resolve_semester(filter_data)
    if not semester:
        return None

    start_date = getattr(semester, "start_date", None)
    if not start_date:
        return None

    delta_days = (reference_date - start_date).days
    if delta_days < 0:
        delta_days = 0
    weeks_since_start = delta_days // 7
    if weeks_since_start % 2 == 0:
        return ClassSession.WeekTypeChoices.ODD
    return ClassSession.WeekTypeChoices.EVEN


def _resolve_semester(filter_data: Any) -> Semester | None:
    candidate = _get_value(filter_data, "filter_semester") or _get_value(filter_data, "semester")
    semester = _normalise_semester(candidate)
    if semester:
        return semester

    candidate_id = _get_value(filter_data, "filter_semester_id") or _get_value(
        filter_data, "semester_id"
    )
    semester = _normalise_semester(candidate_id)
    if semester:
        return semester

    institution = _get_value(filter_data, "institution")
    if institution:
        return semester_repository.get_active_semester(institution)
    return None


def _normalise_semester(value: Any) -> Semester | None:
    if isinstance(value, Semester):
        return value
    if value in (None, ""):
        return None
    try:
        semester_id = int(value)
    except (TypeError, ValueError):
        return None
    return Semester.objects.filter(pk=semester_id, is_deleted=False).first()
    return None
