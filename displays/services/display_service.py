from __future__ import annotations

"""Display screen service helpers for building real-time timetable payloads.

این ماژول تمام منطق مربوط به صفحه‌نمایش‌های عمومی را شامل می‌شود؛ از ایجاد و
به‌روزرسانی تنظیمات نمایش گرفته تا ساخت خروجی کش‌شده برای سامانه‌های
دیجیتال ساینج. توابع موجود ضمن اعتبارسنجی داده‌ها، کش را مدیریت کرده و
دسترسی به پایگاه داده را از طریق لایهٔ مخزن هماهنگ می‌کنند.
"""

from datetime import date, time as time_cls, timedelta
from typing import Iterable, List

from django.db.models import QuerySet
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError

from displays import repositories as display_repository
from displays.models import DisplayScreen
from displays.models.display_models import PY_WEEKDAY_TO_PERSIAN
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
from schedules.models import (
    ClassSession,
    ClassCancellation,
    MakeupClassSession,
)

PERSIAN_TO_PY_WEEKDAY = {value: key for key, value in PY_WEEKDAY_TO_PERSIAN.items()}

DAY_ORDER = {value: index for index, (value, _) in enumerate(ClassSession.DAY_OF_WEEK_CHOICES)}


def _ensure_institution(institution) -> None:
    """اطمینان می‌دهد که عملیات به یک مؤسسه معتبر مرتبط است.

    Args:
        institution: نمونهٔ مؤسسه یا ``None`` اگر کاربر احراز هویت نشده باشد.

    Raises:
        CustomValidationError: زمانی که مؤسسه ارائه نشده باشد تا مصرف‌کننده خطای
        قابل‌درک API دریافت کند.
    """
    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_REQUIRED["message"],
            code=ErrorCodes.INSTITUTION_REQUIRED["code"],
            status_code=ErrorCodes.INSTITUTION_REQUIRED["status_code"],
            errors=ErrorCodes.INSTITUTION_REQUIRED["errors"],
            data=ErrorCodes.INSTITUTION_REQUIRED["data"],
        )


def _validate_serializer(serializer) -> None:
    """Execute serializer validation and normalise any errors.

    Args:
        serializer: نمونهٔ سریالایزر DRF که باید اعتبارسنجی شود.

    Raises:
        CustomValidationError: اگر ``is_valid`` خروجی ناموفق داشته باشد.
    """
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )


def list_display_screens(institution) -> QuerySet[DisplayScreen]:
    """Return the screen queryset for the requesting institution.

    Pagination is applied at the view layer via :func:`BaseResponse.paginate_queryset`
    to leverage the shared response envelope while keeping the repository focused on
    queryset construction.
    
    Args:
        institution: مؤسسهٔ مالک صفحه‌نمایش‌ها.

    Returns:
        QuerySet[DisplayScreen]: کوئری‌ستی آماده برای صفحه‌بندی در لایهٔ بالاتر.

    Raises:
        CustomValidationError: اگر کاربر فاقد مؤسسه معتبر باشد.
    """

    _ensure_institution(institution)
    return display_repository.list_display_screens(institution)


def create_display_screen(data: dict, institution) -> dict:
    """Create a display screen scoped to the given institution.

    Args:
        data: داده‌های خام شامل تنظیمات صفحه‌نمایش.
        institution: مؤسسهٔ مالک صفحه‌نمایش.

    Returns:
        dict: خروجی سریال‌شدهٔ صفحه‌نمایش تازه ایجاد شده.
    """

    _ensure_institution(institution)
    serializer = DisplayScreenWriteSerializer(data=data, context={"institution": institution})
    _validate_serializer(serializer)
    screen = serializer.save(institution=institution)
    return DisplayScreenSerializer(screen).data


def get_display_screen_instance_or_404(screen_id: int, institution) -> DisplayScreen:
    """Fetch a screen instance or raise a structured error.

    Args:
        screen_id: شناسهٔ صفحه‌نمایش.
        institution: مؤسسهٔ مالک که باید با رکورد هم‌خوان باشد.

    Returns:
        DisplayScreen: نمونهٔ مدل در صورت وجود.

    Raises:
        CustomValidationError: اگر صفحه‌نمایش پیدا نشود یا به مؤسسهٔ دیگری تعلق داشته باشد.
    """

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
    """Return serialized data for a screen after ownership validation."""

    screen = get_display_screen_instance_or_404(screen_id, institution)
    return DisplayScreenSerializer(screen).data


def update_display_screen(screen: DisplayScreen, data: dict) -> dict:
    """Apply partial updates to a screen and refresh its cache entry.

    Args:
        screen: نمونهٔ صفحه‌نمایش فعلی.
        data: داده‌های جدید برای به‌روزرسانی (می‌تواند جزئی باشد).

    Returns:
        dict: خروجی سریال‌شدهٔ صفحه‌نمایش پس از ذخیره.
    """

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
    """Soft delete a screen and purge any cached payloads."""

    slug = screen.slug
    display_repository.soft_delete_display_screen(screen)
    cache.delete(f"display:{slug}")


def get_display_screen_by_slug_or_404(slug: str) -> DisplayScreen:
    """Return a screen by slug regardless of authentication context.

    Args:
        slug: شناسهٔ متنی که در URL عمومی استفاده می‌شود.

    Returns:
        DisplayScreen: نمونهٔ صفحه‌نمایش فعال.

    Raises:
        CustomValidationError: اگر صفحه‌نمایش یافت نشود.
    """

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

    Args:
        qs: کوئری‌ست اولیه‌ای که قرار است فیلتر شود.
        week_type: مقدار انتخابی (odd/even/every) یا ``None``.

    Returns:
        QuerySet: کوئری‌ست فیلترشده بر اساس نوع هفته.
    """
    if not week_type:
        return qs
    if week_type == ClassSession.WeekTypeChoices.EVERY:
        return qs.filter(week_type=ClassSession.WeekTypeChoices.EVERY)
    return qs.filter(
        Q(week_type=week_type) | Q(week_type=ClassSession.WeekTypeChoices.EVERY)
    )


def _base_session_queryset(screen: DisplayScreen):
    """Construct the base queryset for class sessions tied to a screen.

    Args:
        screen: نمونهٔ صفحه‌نمایش که مؤسسهٔ آن برای فیلتر استفاده می‌شود.

    Returns:
        QuerySet: کوئری‌ست اولیه با ``select_related`` مناسب برای کاهش تعداد کوئری‌ها.
    """
    return (
        ClassSession.objects.filter(
            institution=screen.institution,
            is_deleted=False,
        )
        .select_related("course", "professor", "classroom__building", "semester")
    )


def _sort_sessions(sessions: Iterable[dict]) -> List[dict]:
    """Sort session payloads deterministically for display stability.

    Args:
        sessions: iterable‌ای از دیکشنری‌ها که شامل داده‌های جلسه هستند.

    Returns:
        List[dict]: نسخه مرتب‌شده بر اساس تاریخ، روز، زمان و عنوان درس.
    """

    def _normalise_date(value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:  # pragma: no cover - defensive
                return date.min
        return date.min

    def _normalise_time(value):
        if value:
            return value
        return time_cls.min

    return sorted(
        sessions,
        key=lambda item: (
            _normalise_date(item.get("date")),
            DAY_ORDER.get(item.get("day_of_week"), 0),
            _normalise_time(item.get("start_time")),
            item.get("course_title", ""),
            item.get("status", ""),
        ),
    )


def _resolve_target_date(screen: DisplayScreen, computed_day: str | None) -> date | None:
    """Determine the calendar date that should anchor the payload.

    Args:
        screen: صفحه‌نمایشی که تنظیمات فیلتر از آن خوانده می‌شود.
        computed_day: مقدار روز هفته (به فارسی) که از تنظیمات محاسبه شده است.

    Returns:
        date | None: تاریخ هدف یا ``None`` اگر نیازی به محدودسازی روز نباشد.
    """
    override = parse_date(screen.filter_date_override)
    if override:
        return override

    if computed_day or screen.filter_use_current_day_of_week or screen.filter_use_current_week_type:
        base_date = timezone.localdate()
        if computed_day:
            weekday = PERSIAN_TO_PY_WEEKDAY.get(computed_day)
            if weekday is not None:
                delta = weekday - base_date.weekday()
                if delta < 0:
                    delta += 7
                return base_date + timedelta(days=delta)
        return base_date
    return None


def _load_cancellations(
    screen: DisplayScreen, sessions: Iterable[ClassSession], target_date: date | None
):
    """Load cancellation instances relevant to the computed session set.

    Args:
        screen: صفحه‌نمایشی که مؤسسه‌اش مبنای جستجو قرار می‌گیرد.
        sessions: لیست جلسات اصلی که شناسهٔ آن‌ها برای فیلتر استفاده می‌شود.
        target_date: تاریخ هدف برای محدودسازی لغوها.

    Returns:
        dict[int, ClassCancellation]: نگاشت شناسهٔ جلسه به شیء لغو متناظر.
    """
    if not target_date:
        return {}
    session_ids = [session.id for session in sessions]
    if not session_ids:
        return {}
    cancellations = (
        ClassCancellation.objects.filter(
            institution=screen.institution,
            class_session_id__in=session_ids,
            date=target_date,
            is_deleted=False,
        )
        .select_related("class_session__professor", "class_session__course")
    )
    return {cancellation.class_session_id: cancellation for cancellation in cancellations}


def _build_session_payload(
    session: ClassSession,
    *,
    target_date: date | None,
    cancellation: ClassCancellation | None,
) -> dict:
    """Construct the API payload for a canonical class session.

    Args:
        session: نمونهٔ جلسه.
        target_date: تاریخ نهایی نمایش داده شده.
        cancellation: لغو متناظر (در صورت وجود).

    Returns:
        dict: ساختار داده‌ای آماده برای سریالایزر عمومی.
    """
    professor = session.professor
    classroom = session.classroom
    building = classroom.building if classroom else None
    note = session.note or ""
    cancellation_note = None
    cancellation_reason = None
    status = "scheduled"
    if cancellation:
        cancellation_reason = cancellation.reason or None
        cancellation_note = cancellation.note or None
        if cancellation_note:
            note = cancellation_note
        status = "cancelled"

    return {
        "id": session.id,
        "session_id": session.id,
        "course_title": session.course.title,
        "professor_name": f"{professor.first_name} {professor.last_name}".strip(),
        "day_of_week": session.day_of_week,
        "start_time": session.start_time,
        "end_time": session.end_time,
        "week_type": session.week_type,
        "classroom_title": classroom.title if classroom else None,
        "building_title": building.title if building else None,
        "group_code": session.group_code,
        "note": note,
        "date": target_date,
        "is_cancelled": bool(cancellation),
        "cancellation_reason": cancellation_reason,
        "cancellation_note": cancellation_note,
        "status": status,
        "is_makeup": False,
        "makeup_for_session_id": None,
    }


def _week_type_for_date(semester, target_date: date | None) -> str | None:
    """Compute the week type (odd/even) for a specific calendar date.

    Args:
        semester: نمونهٔ ترم مرتبط با جلسهٔ کلاس.
        target_date: تاریخی که باید نوع هفته برای آن تعیین شود.

    Returns:
        str | None: مقدار نوع هفته یا ``None`` اگر محاسبه امکان‌پذیر نباشد.
    """
    if not semester or not target_date:
        return None
    start_date = getattr(semester, "start_date", None)
    if not start_date:
        return None
    delta_days = (target_date - start_date).days
    if delta_days < 0:
        delta_days = 0
    weeks_since_start = delta_days // 7
    if weeks_since_start % 2 == 0:
        return ClassSession.WeekTypeChoices.ODD
    return ClassSession.WeekTypeChoices.EVEN


def _makeup_matches_week_type(
    *,
    screen_week_type: str | None,
    session_week_type: str,
    date_week_type: str | None,
) -> bool:
    """Determine whether a makeup session satisfies week-type filters.

    Args:
        screen_week_type: نوع هفته انتخاب‌شده در تنظیمات صفحه.
        session_week_type: نوع هفتهٔ جلسهٔ پایه.
        date_week_type: نوع هفته محاسبه‌شده برای تاریخ خاص.

    Returns:
        bool: ``True`` اگر جلسهٔ جبرانی باید در خروجی باقی بماند.
    """
    if not screen_week_type or screen_week_type == ClassSession.WeekTypeChoices.EVERY:
        return True
    valid_types = {screen_week_type, ClassSession.WeekTypeChoices.EVERY}
    if session_week_type not in valid_types:
        return False
    if date_week_type is None:
        return screen_week_type == session_week_type
    return date_week_type in valid_types


def _build_makeup_payload(makeup: MakeupClassSession) -> dict:
    """Construct the API payload for a makeup class session.

    Args:
        makeup: نمونهٔ جلسهٔ جبرانی ثبت‌شده.

    Returns:
        dict: دیکشنری آماده برای ادغام با لیست جلسات اصلی.
    """
    session = makeup.class_session
    professor = session.professor
    classroom = makeup.classroom
    building = classroom.building if classroom else None
    semester = session.semester
    week_type = _week_type_for_date(semester, makeup.date)
    return {
        "id": makeup.id,
        "session_id": session.id,
        "course_title": session.course.title,
        "professor_name": f"{professor.first_name} {professor.last_name}".strip(),
        "day_of_week": PY_WEEKDAY_TO_PERSIAN.get(makeup.date.weekday(), session.day_of_week),
        "start_time": makeup.start_time,
        "end_time": makeup.end_time,
        "week_type": week_type or session.week_type,
        "classroom_title": classroom.title if classroom else None,
        "building_title": building.title if building else None,
        "group_code": makeup.group_code or session.group_code,
        "note": makeup.note or session.note or "",
        "date": makeup.date,
        "is_cancelled": False,
        "cancellation_reason": None,
        "cancellation_note": None,
        "status": "makeup",
        "is_makeup": True,
        "makeup_for_session_id": session.id,
    }


def _collect_makeup_payloads(
    screen: DisplayScreen,
    *,
    target_date: date | None,
    computed_week_type: str | None,
) -> List[dict]:
    """Gather serialized payloads for makeup sessions that match filters.

    Args:
        screen: صفحه‌نمایش مبنا.
        target_date: تاریخ انتخاب شده برای نمایش.
        computed_week_type: نوع هفتهٔ استخراج شده از تنظیمات.

    Returns:
        list[dict]: آرایه‌ای از دیکشنری‌های جلسهٔ جبرانی.
    """
    if not target_date:
        return []

    qs = (
        MakeupClassSession.objects.filter(
            institution=screen.institution,
            is_deleted=False,
            date=target_date,
        )
        .select_related(
            "class_session__course",
            "class_session__professor",
            "class_session__semester",
            "classroom__building",
        )
    )

    if screen.filter_classroom_id:
        qs = qs.filter(classroom_id=screen.filter_classroom_id)

    if screen.filter_building_id:
        qs = qs.filter(classroom__building_id=screen.filter_building_id)

    if screen.filter_course_id:
        qs = qs.filter(class_session__course_id=screen.filter_course_id)

    if screen.filter_professor_id:
        qs = qs.filter(class_session__professor_id=screen.filter_professor_id)

    if screen.filter_semester_id:
        qs = qs.filter(class_session__semester_id=screen.filter_semester_id)

    if screen.filter_start_time:
        qs = qs.filter(start_time__gte=screen.filter_start_time)

    if screen.filter_end_time:
        qs = qs.filter(end_time__lte=screen.filter_end_time)

    payloads: List[dict] = []
    for makeup in qs:
        session = makeup.class_session
        if screen.filter_capacity is not None:
            if session.capacity is None or session.capacity < screen.filter_capacity:
                continue

        if screen.filter_group_code:
            group_code = screen.filter_group_code
            available_codes = {
                code
                for code in [makeup.group_code, session.group_code]
                if code not in (None, "")
            }
            if group_code not in available_codes:
                continue

        week_type_for_date = _week_type_for_date(session.semester, makeup.date)
        if not _makeup_matches_week_type(
            screen_week_type=computed_week_type,
            session_week_type=session.week_type,
            date_week_type=week_type_for_date,
        ):
            continue

        payloads.append(_build_makeup_payload(makeup))

    return payloads

def _collect_sessions_for_screen(screen: DisplayScreen) -> List[ClassSession]:
    """Return all sessions that match the screen filter configuration.

    The function centralises the filtering logic so it can be reused when the
    payload is fetched from cache and when it is rebuilt.  It honours the
    activation flag, the user-provided selectors, and computed fallbacks such
    as day-of-week and week-type rules.

    Args:
        screen: صفحه‌نمایش که فیلترها از آن خوانده می‌شوند.

    Returns:
        list[ClassSession]: لیست جلساتی که معیارها را پاس می‌کنند.
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

    Args:
        screen: صفحه‌نمایش هدف.
        use_cache: آیا از کش استفاده شود یا خیر.

    Returns:
        dict: ساختار کامل شامل متادیتای فیلتر، جلسات و زمان تولید.
    """
    # Cache keys are namespaced with the ``display:`` prefix so they do not
    # collide with other app caches; the slug uniquely identifies each screen.
    cache_key = f"display:{screen.slug}"
    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            return cached

    base_sessions = _collect_sessions_for_screen(screen)
    computed_day = compute_filter_day_of_week(screen)
    computed_week_type = compute_filter_week_type(screen)
    target_date = _resolve_target_date(screen, computed_day)
    cancellations = _load_cancellations(screen, base_sessions, target_date)

    session_payloads = [
        _build_session_payload(
            session,
            target_date=target_date,
            cancellation=cancellations.get(session.id),
        )
        for session in base_sessions
    ]

    makeup_payloads = _collect_makeup_payloads(
        screen,
        target_date=target_date,
        computed_week_type=computed_week_type,
    )

    sessions = _sort_sessions(session_payloads + makeup_payloads)

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
    """Remove the cached payload for the provided screen.

    Args:
        screen: صفحه‌نمایشی که کش آن باید پاک شود.
    """
    # Mirrors the naming strategy in ``build_public_payload`` to target only the
    # affected screen without disturbing other cached responses.
    cache.delete(f"display:{screen.slug}")
