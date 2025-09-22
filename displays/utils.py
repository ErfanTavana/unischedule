from __future__ import annotations

from datetime import date
from typing import Any

from django.utils import timezone

from schedules.models import ClassSession
from semesters.models import Semester

from displays.models.display_models import PY_WEEKDAY_TO_PERSIAN


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


def _resolve_semester(filter_data: Any) -> Semester | None:
    semester = _get_value(filter_data, "filter_semester")
    if isinstance(semester, Semester):
        return semester

    semester_id = semester or _get_value(filter_data, "filter_semester_id")
    if not semester_id:
        return None

    try:
        return Semester.objects.filter(pk=semester_id).first()
    except (TypeError, ValueError):
        return None


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
    return None


def compute_filter_week_type(filter_data: Any) -> str | None:
    week_type = _get_value(filter_data, "week_type") or _get_value(
        filter_data, "filter_week_type"
    )
    if week_type:
        return week_type

    override = parse_date(
        _get_value(filter_data, "date_override")
        or _get_value(filter_data, "filter_date_override")
    )

    semester = _resolve_semester(filter_data)
    if semester:
        reference_date = override or timezone.localdate()
        if reference_date < semester.start_date or reference_date > semester.end_date:
            return None

        weeks_passed = (reference_date - semester.start_date).days // 7
        return (
            ClassSession.WeekTypeChoices.ODD
            if weeks_passed % 2 == 0
            else ClassSession.WeekTypeChoices.EVEN
        )

    if override:
        week_number = override.isocalendar()[1]
        return (
            ClassSession.WeekTypeChoices.ODD
            if week_number % 2
            else ClassSession.WeekTypeChoices.EVEN
        )
    return None
