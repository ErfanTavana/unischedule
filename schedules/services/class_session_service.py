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
    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_REQUIRED["message"],
            code=ErrorCodes.INSTITUTION_REQUIRED["code"],
            status_code=ErrorCodes.INSTITUTION_REQUIRED["status_code"],
            errors=ErrorCodes.INSTITUTION_REQUIRED["errors"],
            data=ErrorCodes.INSTITUTION_REQUIRED["data"],
        )


def _check_conflict(data, institution):
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
    validated_data["institution"] = institution
    _check_conflict(validated_data, institution)
    session = class_session_repository.create_class_session(validated_data)
    invalidate_related_displays(session)
    return ClassSessionSerializer(session).data


def update_class_session(session: ClassSession, data: dict) -> dict:
    _ensure_institution(session.institution)
    serializer = UpdateClassSessionSerializer(instance=session, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )
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
    session = get_class_session_instance_or_404(session_id, institution)
    return ClassSessionSerializer(session).data


def delete_class_session(session: ClassSession) -> None:
    _ensure_institution(session.institution)
    class_session_repository.soft_delete_class_session(session)
    invalidate_related_displays(session)


def list_class_sessions(institution) -> list[dict]:
    _ensure_institution(institution)
    queryset = class_session_repository.list_class_sessions_by_institution(institution)
    return ClassSessionSerializer(queryset, many=True).data
