from __future__ import annotations

from datetime import date, time

from django.db.models import Q, QuerySet

from schedules.models import ClassCancellation, MakeupClassSession


# --- Class cancellation operations ------------------------------------------

def create_class_cancellation(data: dict) -> ClassCancellation:
    """یک رکورد لغو کلاس را با داده‌های دریافتی ایجاد می‌کند."""

    return ClassCancellation.objects.create(**data)


def update_class_cancellation_fields(
    cancellation: ClassCancellation, fields: dict
) -> ClassCancellation:
    """فیلدهای دلخواه لغو کلاس را به‌روزرسانی و نمونهٔ ذخیره‌شده را بازمی‌گرداند."""

    for key, value in fields.items():
        setattr(cancellation, key, value)
    cancellation.save()
    return cancellation


def get_class_cancellation_by_id_and_institution(
    cancellation_id: int, institution
) -> ClassCancellation | None:
    """لغو کلاس مربوط به شناسه و مؤسسهٔ مشخص را جست‌وجو می‌کند."""

    return (
        ClassCancellation.objects.filter(
            id=cancellation_id,
            institution=institution,
            is_deleted=False,
        )
        .select_related("class_session__course", "class_session__professor")
        .first()
    )


def list_class_cancellations_by_institution(institution) -> QuerySet[ClassCancellation]:
    """تمام لغوهای فعال یک مؤسسه را با روابط مورد نیاز برای نمایش بازمی‌گرداند."""

    return ClassCancellation.objects.filter(
        institution=institution,
        is_deleted=False,
    ).select_related(
        "class_session__course",
        "class_session__professor",
        "class_session__classroom__building",
    )


def soft_delete_class_cancellation(cancellation: ClassCancellation) -> None:
    """لغو کلاس را به صورت نرم حذف می‌کند تا در لیست نتایج نمایش داده نشود."""

    cancellation.delete()


def cancellation_exists_for_session_and_date(
    *,
    class_session_id: int,
    cancellation_date: date,
    institution,
    exclude_id: int | None = None,
) -> bool:
    """آیا در همان تاریخ برای جلسهٔ موردنظر قبلاً لغوی ثبت شده است یا خیر."""

    qs = ClassCancellation.objects.filter(
        class_session_id=class_session_id,
        date=cancellation_date,
        institution=institution,
        is_deleted=False,
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return qs.exists()


# --- Makeup session operations ---------------------------------------------

def create_makeup_class_session(data: dict) -> MakeupClassSession:
    """یک جلسهٔ جبرانی جدید بر اساس داده‌های اعتبارسنجی‌شده می‌سازد."""

    return MakeupClassSession.objects.create(**data)


def update_makeup_class_session_fields(
    makeup_session: MakeupClassSession, fields: dict
) -> MakeupClassSession:
    """فیلدهای جلسهٔ جبرانی را تغییر داده و نمونهٔ بروزشده را بازمی‌گرداند."""

    for key, value in fields.items():
        setattr(makeup_session, key, value)
    makeup_session.save()
    return makeup_session


def get_makeup_class_session_by_id_and_institution(
    makeup_id: int, institution
) -> MakeupClassSession | None:
    """جلسهٔ جبرانی متعلق به مؤسسه و شناسهٔ داده شده را بازیابی می‌کند."""

    return (
        MakeupClassSession.objects.filter(
            id=makeup_id,
            institution=institution,
            is_deleted=False,
        )
        .select_related(
            "class_session__course",
            "class_session__professor",
            "class_session__classroom__building",
            "classroom__building",
        )
        .first()
    )


def list_makeup_class_sessions_by_institution(
    institution,
) -> QuerySet[MakeupClassSession]:
    """جلسات جبرانی فعال یک مؤسسه را به همراه روابط کلیدی برای مصرف API فراهم می‌کند."""

    return MakeupClassSession.objects.filter(
        institution=institution,
        is_deleted=False,
    ).select_related(
        "class_session__course",
        "class_session__professor",
        "class_session__classroom__building",
        "classroom__building",
    )


def soft_delete_makeup_class_session(makeup_session: MakeupClassSession) -> None:
    """جلسهٔ جبرانی را بدون حذف نهایی از پایگاه داده علامت حذف می‌کند."""

    makeup_session.delete()


def makeup_time_conflict_exists(
    *,
    institution,
    class_session_id: int,
    classroom_id: int,
    professor_id: int,
    target_date: date,
    start_time: time,
    end_time: time,
    exclude_id: int | None = None,
) -> bool:
    """وجود تداخل زمانی بین جلسهٔ جبرانی مورد نظر و سایر جلسات فعال را بررسی می‌کند."""

    overlap = Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    qs = MakeupClassSession.objects.filter(
        institution=institution,
        date=target_date,
        is_deleted=False,
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    qs = qs.filter(overlap)
    return qs.filter(
        Q(classroom_id=classroom_id)
        | Q(class_session__professor_id=professor_id)
        | Q(class_session_id=class_session_id)
    ).exists()

