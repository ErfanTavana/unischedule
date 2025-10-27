from __future__ import annotations

from datetime import date, time

from django.db.models import Q, QuerySet

from schedules.models import ClassCancellation, MakeupClassSession


# --- Class cancellation operations ------------------------------------------

def create_class_cancellation(data: dict) -> ClassCancellation:
    return ClassCancellation.objects.create(**data)


def update_class_cancellation_fields(
    cancellation: ClassCancellation, fields: dict
) -> ClassCancellation:
    for key, value in fields.items():
        setattr(cancellation, key, value)
    cancellation.save()
    return cancellation


def get_class_cancellation_by_id_and_institution(
    cancellation_id: int, institution
) -> ClassCancellation | None:
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
    return ClassCancellation.objects.filter(
        institution=institution,
        is_deleted=False,
    ).select_related(
        "class_session__course",
        "class_session__professor",
        "class_session__classroom__building",
    )


def soft_delete_class_cancellation(cancellation: ClassCancellation) -> None:
    cancellation.delete()


def cancellation_exists_for_session_and_date(
    *,
    class_session_id: int,
    cancellation_date: date,
    institution,
    exclude_id: int | None = None,
) -> bool:
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
    return MakeupClassSession.objects.create(**data)


def update_makeup_class_session_fields(
    makeup_session: MakeupClassSession, fields: dict
) -> MakeupClassSession:
    for key, value in fields.items():
        setattr(makeup_session, key, value)
    makeup_session.save()
    return makeup_session


def get_makeup_class_session_by_id_and_institution(
    makeup_id: int, institution
) -> MakeupClassSession | None:
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

