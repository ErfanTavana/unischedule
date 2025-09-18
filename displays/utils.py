from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from schedules.models import ClassSession

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


def compute_filter_day_of_week(filter_data: dict[str, Any]) -> str | None:
    day = filter_data.get("day_of_week")
    if day:
        return day
    override = parse_date(filter_data.get("date_override"))
    if override:
        return PY_WEEKDAY_TO_PERSIAN.get(override.weekday())
    return None


def compute_filter_week_type(filter_data: dict[str, Any]) -> str | None:
    week_type = filter_data.get("week_type")
    if week_type:
        return week_type
    override = parse_date(filter_data.get("date_override"))
    if override:
        week_number = override.isocalendar()[1]
        return (
            ClassSession.WeekTypeChoices.ODD
            if week_number % 2
            else ClassSession.WeekTypeChoices.EVEN
        )
    return None


def sort_filters(filters: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        list(filters),
        key=lambda item: (
            item.get("position", 0),
            str(item.get("id", "")),
        ),
    )
