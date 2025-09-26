from __future__ import annotations

from datetime import date
from typing import Any

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
    return None


def compute_filter_week_type(filter_data: Any) -> str | None:
    week_type = _get_value(filter_data, "week_type") or _get_value(
        filter_data, "filter_week_type"
    )
    if week_type:
        return week_type
    return None
