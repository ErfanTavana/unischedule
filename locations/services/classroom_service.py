from locations.repositories import classroom_repository
from locations.serializers.classroom_serializer import (
    ClassroomSerializer,
    CreateClassroomSerializer,
    UpdateClassroomSerializer,
)
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError


def create_classroom(data: dict, building) -> dict:
    """Create a classroom after validating required fields.

    ``CreateClassroomSerializer`` checks that a title is provided before the
    room is associated with the supplied building, ensuring incomplete payloads
    are rejected prior to persistence.
    """
    serializer = CreateClassroomSerializer(data=data)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated_data = serializer.validated_data
    validated_data["building"] = building

    classroom = classroom_repository.create_classroom(validated_data)
    return ClassroomSerializer(classroom).data


def get_classroom_instance_or_404(classroom_id: int, building):
    """Retrieve a classroom belonging to the building or raise an error.

    Only returns classrooms linked to the provided building and not soft
    deleted, so it validates both ownership and active status.
    """
    classroom = classroom_repository.get_classroom_by_id_and_building(classroom_id, building)
    if not classroom:
        raise CustomValidationError(
            message=ErrorCodes.CLASSROOM_NOT_FOUND["message"],
            code=ErrorCodes.CLASSROOM_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASSROOM_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASSROOM_NOT_FOUND["errors"],
        )
    return classroom


def get_classroom_by_id_or_404(classroom_id: int, building) -> dict:
    """Return serialized classroom data after building membership validation.

    Ensures the classroom exists within the supplied building before
    serialization, preventing information leaks across buildings.
    """
    classroom = get_classroom_instance_or_404(classroom_id, building)
    return ClassroomSerializer(classroom).data


def update_classroom(classroom, data: dict) -> dict:
    """Update classroom fields while validating incoming changes.

    The ``UpdateClassroomSerializer`` performs partial validation (e.g. title
    cannot be blank) before saving, protecting against invalid edits.
    """
    serializer = UpdateClassroomSerializer(instance=classroom, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    updated_instance = serializer.save()
    return ClassroomSerializer(updated_instance).data


def delete_classroom(classroom) -> None:
    """Soft delete an institution-approved classroom instance.

    The caller must fetch the classroom through the institution-aware helpers
    so we only mark authorized records as deleted.
    """
    classroom_repository.soft_delete_classroom(classroom)


def list_classrooms_for_institution(institution) -> list[dict]:
    """List active classrooms across all buildings of the institution.

    Uses repository filtering to include only classrooms tied to the
    institution's buildings with ``is_deleted=False``.
    """
    queryset = classroom_repository.list_classrooms_by_institution(institution)
    return ClassroomSerializer(queryset, many=True).data


def list_classrooms(building) -> list[dict]:
    """List active classrooms for a building, excluding soft-deleted ones.

    The repository query scopes by building and ``is_deleted=False`` to only
    expose currently available rooms.
    """
    queryset = classroom_repository.list_classrooms_by_building(building)
    return ClassroomSerializer(queryset, many=True).data


def get_classroom_by_id_and_institution_or_404(classroom_id: int, institution) -> dict:
    """Serialize a classroom after confirming institution ownership.

    Ensures the classroom exists, belongs to the institution and is active
    before exposing its data to the caller.
    """
    classroom = classroom_repository.get_classroom_by_id_and_institution(classroom_id, institution)

    if not classroom:
        raise CustomValidationError(
            message=ErrorCodes.CLASSROOM_NOT_FOUND["message"],
            code=ErrorCodes.CLASSROOM_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASSROOM_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASSROOM_NOT_FOUND["errors"]
        )

    return ClassroomSerializer(classroom).data


def get_classroom_instance_by_institution_or_404(classroom_id: int, institution):
    """Return a classroom instance tied to the institution or raise an error.

    Limits access to classrooms linked to the institution and not soft-deleted,
    safeguarding against cross-institution edits or deletions.
    """
    classroom = classroom_repository.get_classroom_by_id_and_institution(classroom_id, institution)

    if not classroom:
        raise CustomValidationError(
            message=ErrorCodes.CLASSROOM_NOT_FOUND["message"],
            code=ErrorCodes.CLASSROOM_NOT_FOUND["code"],
            status_code=ErrorCodes.CLASSROOM_NOT_FOUND["status_code"],
            errors=ErrorCodes.CLASSROOM_NOT_FOUND["errors"]
        )
    return classroom
