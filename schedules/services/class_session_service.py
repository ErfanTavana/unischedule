"""Service functions that manage recurring class sessions for institutions.

این ماژول مسئولیت اعتبارسنجی، جلوگیری از تداخل زمانی و همگام‌سازی کش نمایش‌ها
را بر عهده دارد تا عملیات CRUD روی جلسات کلاس با ثبات و مستند انجام شود.
"""

from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes
from schedules.serializers import (
    CreateClassSessionSerializer,
    UpdateClassSessionSerializer,
    ClassSessionSerializer,
)
from schedules import repositories as class_session_repository
from schedules.models import ClassSession
from schedules.services.display_invalidation import invalidate_related_displays


def _ensure_institution(institution) -> None:
    """اطمینان حاصل می‌کند که درخواست به یک مؤسسه معتبر متصل است.

    Args:
        institution: نمونهٔ مؤسسه یا مقدار ``None``.

    Raises:
        CustomValidationError: اگر مؤسسه ارائه نشده باشد.
    """

    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_REQUIRED["message"],
            code=ErrorCodes.INSTITUTION_REQUIRED["code"],
            status_code=ErrorCodes.INSTITUTION_REQUIRED["status_code"],
            errors=ErrorCodes.INSTITUTION_REQUIRED["errors"],
            data=ErrorCodes.INSTITUTION_REQUIRED["data"],
        )


def _check_conflict(data, institution):
    """بررسی می‌کند که زمان‌بندی کلاس با سایر جلسات در همان موسسه تداخل نداشته باشد.

    Args:
        data: داده‌های معتبرشدهٔ جلسه که باید بررسی شوند.
        institution: مؤسسه‌ای که جلسه به آن تعلق دارد.

    Raises:
        CustomValidationError: اگر بازهٔ زمانی انتخابی با جلسه دیگری هم‌پوشانی داشته باشد.
    """
    if class_session_repository.has_time_conflict(
        institution=institution,
        semester=data["semester"],
        day_of_week=data["day_of_week"],
        start_time=data["start_time"],
        end_time=data["end_time"],
        week_type=data.get("week_type", ClassSession.WeekTypeChoices.EVERY),
        classroom=data["classroom"],
        professor=data["professor"],
        exclude_id=data.get("id"),
    ):
        raise CustomValidationError(
            message=ErrorCodes.CLASS_SESSION_CONFLICT["message"],
            code=ErrorCodes.CLASS_SESSION_CONFLICT["code"],
            status_code=ErrorCodes.CLASS_SESSION_CONFLICT["status_code"],
            errors=ErrorCodes.CLASS_SESSION_CONFLICT["errors"],
        )


def create_class_session(data: dict, institution) -> dict:
    """یک جلسهٔ جدید ایجاد می‌کند و قبل از ذخیره از نبود تداخل زمانی اطمینان می‌یابد.

    Args:
        data: دیکشنری داده‌های خام دریافتی از درخواست.
        institution: مؤسسهٔ مالک جلسه.

    Returns:
        dict: دادهٔ سریال‌شدهٔ جلسهٔ تازه ایجاد شده.

    Raises:
        CustomValidationError: در صورت شکست اعتبارسنجی یا بروز تداخل زمانی.
    """
    _ensure_institution(institution)
    serializer = CreateClassSessionSerializer(data=data)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )
    validated_data = serializer.validated_data
    # موسسه از درخواست استخراج و به داده‌های معتبر شده افزوده می‌شود
    validated_data["institution"] = institution
    _check_conflict(validated_data, institution)
    session = class_session_repository.create_class_session(validated_data)
    invalidate_related_displays(session)
    return ClassSessionSerializer(session).data


def update_class_session(session: ClassSession, data: dict) -> dict:
    """یک جلسهٔ موجود را با داده‌های جدید به‌روزرسانی کرده و هرگونه تداخل احتمالی را بررسی می‌کند.

    Args:
        session: نمونهٔ فعلی جلسهٔ کلاس.
        data: داده‌های ورودی برای به‌روزرسانی.

    Returns:
        dict: خروجی سریال‌شده پس از ذخیرهٔ تغییرات.

    Raises:
        CustomValidationError: در صورت شکست اعتبارسنجی یا تشخیص تداخل زمانی.
    """
    _ensure_institution(session.institution)
    serializer = UpdateClassSessionSerializer(instance=session, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )
    # نسخهٔ اصلی برای ثبت وضعیت پیش از تغییر نگه‌داری می‌شود تا کش نمایش‌ها نیز به‌روزرسانی گردد
    original_session = ClassSession.objects.get(pk=session.pk)
    validated_data = serializer.validated_data
    validated_data["id"] = session.id
    validated_data.setdefault("institution", session.institution)
    _check_conflict(validated_data, session.institution)
    updated_instance = serializer.save()
    invalidate_related_displays(updated_instance)
    invalidate_related_displays(original_session)
    return ClassSessionSerializer(updated_instance).data


def get_class_session_instance_or_404(session_id: int, institution) -> ClassSession:
    """نمونهٔ مدل را با اعتبارسنجی مؤسسه بازیابی کرده یا خطای دامنه‌ای پرتاب می‌کند.

    Args:
        session_id: شناسهٔ جلسهٔ مدنظر.
        institution: مؤسسهٔ مالک.

    Returns:
        ClassSession: نمونهٔ مدل در صورت وجود.

    Raises:
        CustomValidationError: اگر جلسه یافت نشود یا به مؤسسه تعلق نداشته باشد.
    """

    _ensure_institution(institution)
    session = class_session_repository.get_class_session_by_id_and_institution(session_id, institution)
    if not session:
        raise CustomValidationError(
            message=ErrorCodes.CLASS_SESSION_NOT_FOUND["message"],
            code=ErrorCodes.CLASS_SESSION_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASS_SESSION_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASS_SESSION_NOT_FOUND["errors"],
        )
    return session


def get_class_session_by_id_or_404(session_id: int, institution) -> dict:
    """دادهٔ سریال‌شدهٔ جلسه را در صورت وجود و تعلق به مؤسسه بازمی‌گرداند.

    Args:
        session_id: شناسهٔ جلسهٔ مورد نظر.
        institution: مؤسسهٔ درخواست‌کننده.

    Returns:
        dict: خروجی سریال‌شدهٔ جلسه.
    """

    session = get_class_session_instance_or_404(session_id, institution)
    return ClassSessionSerializer(session).data


def delete_class_session(session: ClassSession) -> None:
    """جلسهٔ داده‌شده را حذف نرم کرده و کش نمایش‌های مرتبط را نامعتبر می‌کند.

    Args:
        session: نمونهٔ جلسه‌ای که باید حذف نرم شود.
    """

    _ensure_institution(session.institution)
    class_session_repository.soft_delete_class_session(session)
    invalidate_related_displays(session)


def list_class_sessions(institution) -> list[dict]:
    """لیست سریال‌شدهٔ جلسات فعال مؤسسهٔ ورودی را تولید می‌کند.

    Args:
        institution: مؤسسهٔ مالک جلسات.

    Returns:
        list[dict]: لیست داده‌های سریال‌شده برای پاسخ API.
    """

    _ensure_institution(institution)
    queryset = class_session_repository.list_class_sessions_by_institution(institution)
    return ClassSessionSerializer(queryset, many=True).data
