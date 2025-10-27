from __future__ import annotations

from datetime import date

from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError
from schedules.models import ClassSession, ClassCancellation, MakeupClassSession
from schedules.serializers import (
    ClassCancellationSerializer,
    CreateClassCancellationSerializer,
    UpdateClassCancellationSerializer,
    MakeupClassSessionSerializer,
    CreateMakeupClassSessionSerializer,
    UpdateMakeupClassSessionSerializer,
)
from schedules import repositories as schedule_repository
from schedules.services.display_invalidation import invalidate_related_displays


def _ensure_institution(institution) -> None:
    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_REQUIRED["message"],
            code=ErrorCodes.INSTITUTION_REQUIRED["code"],
            status_code=ErrorCodes.INSTITUTION_REQUIRED["status_code"],
            errors=ErrorCodes.INSTITUTION_REQUIRED["errors"],
            data=ErrorCodes.INSTITUTION_REQUIRED["data"],
        )


def _ensure_session_institution(session: ClassSession, institution) -> None:
    if session.institution_id != getattr(institution, "id", None):
        raise CustomValidationError(
            message=ErrorCodes.CLASS_SESSION_NOT_FOUND["message"],
            code=ErrorCodes.CLASS_SESSION_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASS_SESSION_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASS_SESSION_NOT_FOUND["errors"],
        )


# ---------------------------------------------------------------------------
# Class cancellation service helpers


def _check_duplicate_cancellation(
    *,
    session: ClassSession,
    institution,
    cancellation_date: date,
    exclude_id: int | None = None,
) -> None:
    if schedule_repository.cancellation_exists_for_session_and_date(
        class_session_id=session.id,
        cancellation_date=cancellation_date,
        institution=institution,
        exclude_id=exclude_id,
    ):
        raise CustomValidationError(
            message=ErrorCodes.CLASS_CANCELLATION_CONFLICT["message"],
            code=ErrorCodes.CLASS_CANCELLATION_CONFLICT["code"],
            status_code=ErrorCodes.CLASS_CANCELLATION_CONFLICT["status_code"],
            errors=ErrorCodes.CLASS_CANCELLATION_CONFLICT["errors"],
        )


def create_class_cancellation(data: dict, institution) -> dict:
    _ensure_institution(institution)
    serializer = CreateClassCancellationSerializer(data=data)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated = dict(serializer.validated_data)
    session: ClassSession = validated["class_session"]
    _ensure_session_institution(session, institution)
    _check_duplicate_cancellation(
        session=session,
        institution=institution,
        cancellation_date=validated["date"],
    )

    validated["institution"] = institution
    cancellation = schedule_repository.create_class_cancellation(validated)
    invalidate_related_displays(session, force=True)
    return ClassCancellationSerializer(cancellation).data


def update_class_cancellation(
    cancellation: ClassCancellation, data: dict
) -> dict:
    _ensure_institution(cancellation.institution)
    serializer = UpdateClassCancellationSerializer(
        instance=cancellation,
        data=data,
        partial=True,
    )
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    original_session = cancellation.class_session
    updated_session = serializer.validated_data.get("class_session", original_session)
    _ensure_session_institution(updated_session, cancellation.institution)
    cancellation_date = serializer.validated_data.get("date", cancellation.date)
    _check_duplicate_cancellation(
        session=updated_session,
        institution=cancellation.institution,
        cancellation_date=cancellation_date,
        exclude_id=cancellation.id,
    )

    updated = serializer.save()
    invalidate_related_displays(original_session, force=True)
    if original_session.id != updated_session.id:
        invalidate_related_displays(updated_session, force=True)
    return ClassCancellationSerializer(updated).data


def list_class_cancellations(institution) -> list[dict]:
    _ensure_institution(institution)
    queryset = schedule_repository.list_class_cancellations_by_institution(institution)
    return ClassCancellationSerializer(queryset, many=True).data


def get_class_cancellation_instance_or_404(
    cancellation_id: int, institution
) -> ClassCancellation:
    _ensure_institution(institution)
    cancellation = schedule_repository.get_class_cancellation_by_id_and_institution(
        cancellation_id,
        institution,
    )
    if not cancellation:
        raise CustomValidationError(
            message=ErrorCodes.CLASS_CANCELLATION_NOT_FOUND["message"],
            code=ErrorCodes.CLASS_CANCELLATION_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASS_CANCELLATION_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASS_CANCELLATION_NOT_FOUND["errors"],
        )
    return cancellation


def get_class_cancellation_by_id_or_404(cancellation_id: int, institution) -> dict:
    cancellation = get_class_cancellation_instance_or_404(cancellation_id, institution)
    return ClassCancellationSerializer(cancellation).data


def delete_class_cancellation(cancellation: ClassCancellation) -> None:
    _ensure_institution(cancellation.institution)
    schedule_repository.soft_delete_class_cancellation(cancellation)
    invalidate_related_displays(cancellation.class_session, force=True)


# ---------------------------------------------------------------------------
# Makeup class session service helpers


def _check_makeup_conflict(
    *,
    session: ClassSession,
    makeup_date: date,
    start_time,
    end_time,
    classroom,
    institution,
    exclude_id: int | None = None,
) -> None:
    if schedule_repository.makeup_time_conflict_exists(
        institution=institution,
        class_session_id=session.id,
        classroom_id=classroom.id,
        professor_id=session.professor_id,
        target_date=makeup_date,
        start_time=start_time,
        end_time=end_time,
        exclude_id=exclude_id,
    ):
        raise CustomValidationError(
            message=ErrorCodes.MAKEUP_SESSION_CONFLICT["message"],
            code=ErrorCodes.MAKEUP_SESSION_CONFLICT["code"],
            status_code=ErrorCodes.MAKEUP_SESSION_CONFLICT["status_code"],
            errors=ErrorCodes.MAKEUP_SESSION_CONFLICT["errors"],
        )


def create_makeup_class_session(data: dict, institution) -> dict:
    _ensure_institution(institution)
    serializer = CreateMakeupClassSessionSerializer(
        data=data,
        context={"institution": institution},
    )
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated = dict(serializer.validated_data)
    session: ClassSession = validated["class_session"]
    _ensure_session_institution(session, institution)
    classroom = validated["classroom"]
    if classroom.building.institution_id != institution.id:
        raise CustomValidationError(
            message=ErrorCodes.CLASSROOM_NOT_FOUND["message"],
            code=ErrorCodes.CLASSROOM_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASSROOM_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASSROOM_NOT_FOUND["errors"],
        )

    _check_makeup_conflict(
        session=session,
        makeup_date=validated["date"],
        start_time=validated["start_time"],
        end_time=validated["end_time"],
        classroom=classroom,
        institution=institution,
    )

    if not validated.get("group_code"):
        validated["group_code"] = session.group_code or ""

    validated["institution"] = institution
    makeup = schedule_repository.create_makeup_class_session(validated)
    invalidate_related_displays(session, force=True)
    return MakeupClassSessionSerializer(makeup).data


def update_makeup_class_session(
    makeup_session: MakeupClassSession, data: dict
) -> dict:
    _ensure_institution(makeup_session.institution)
    serializer = UpdateMakeupClassSessionSerializer(
        instance=makeup_session,
        data=data,
        partial=True,
        context={"institution": makeup_session.institution},
    )
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    original_session = makeup_session.class_session
    updated_session = serializer.validated_data.get("class_session", original_session)
    _ensure_session_institution(updated_session, makeup_session.institution)
    classroom = serializer.validated_data.get("classroom", makeup_session.classroom)
    if classroom.building.institution_id != makeup_session.institution.id:
        raise CustomValidationError(
            message=ErrorCodes.CLASSROOM_NOT_FOUND["message"],
            code=ErrorCodes.CLASSROOM_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASSROOM_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASSROOM_NOT_FOUND["errors"],
        )

    makeup_date = serializer.validated_data.get("date", makeup_session.date)
    start_time = serializer.validated_data.get("start_time", makeup_session.start_time)
    end_time = serializer.validated_data.get("end_time", makeup_session.end_time)

    _check_makeup_conflict(
        session=updated_session,
        makeup_date=makeup_date,
        start_time=start_time,
        end_time=end_time,
        classroom=classroom,
        institution=makeup_session.institution,
        exclude_id=makeup_session.id,
    )

    updated = serializer.save()
    invalidate_related_displays(original_session, force=True)
    if original_session.id != updated_session.id:
        invalidate_related_displays(updated_session, force=True)
    else:
        invalidate_related_displays(updated_session)
    return MakeupClassSessionSerializer(updated).data


def list_makeup_class_sessions(institution) -> list[dict]:
    _ensure_institution(institution)
    queryset = schedule_repository.list_makeup_class_sessions_by_institution(institution)
    return MakeupClassSessionSerializer(queryset, many=True).data


def get_makeup_class_session_instance_or_404(
    makeup_id: int, institution
) -> MakeupClassSession:
    _ensure_institution(institution)
    makeup_session = schedule_repository.get_makeup_class_session_by_id_and_institution(
        makeup_id,
        institution,
    )
    if not makeup_session:
        raise CustomValidationError(
            message=ErrorCodes.MAKEUP_SESSION_NOT_FOUND["message"],
            code=ErrorCodes.MAKEUP_SESSION_NOT_FOUND["code"],
            status_code=ErrorCodes.MAKEUP_SESSION_NOT_FOUND["status_code"],
            errors=ErrorCodes.MAKEUP_SESSION_NOT_FOUND["errors"],
        )
    return makeup_session


def get_makeup_class_session_by_id_or_404(makeup_id: int, institution) -> dict:
    makeup_session = get_makeup_class_session_instance_or_404(makeup_id, institution)
    return MakeupClassSessionSerializer(makeup_session).data


def delete_makeup_class_session(makeup_session: MakeupClassSession) -> None:
    _ensure_institution(makeup_session.institution)
    schedule_repository.soft_delete_makeup_class_session(makeup_session)
    invalidate_related_displays(makeup_session.class_session, force=True)
