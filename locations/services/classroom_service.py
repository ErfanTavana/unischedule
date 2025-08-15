from locations.repositories import classroom_repository
from locations.serializers.classroom_serializer import (
    ClassroomSerializer,
    CreateClassroomSerializer,
    UpdateClassroomSerializer,
)
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes


def create_classroom(data: dict, building) -> dict:
    """
    Create a new classroom for a given building.
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
    """
    Retrieve classroom instance by ID and building or raise error.
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
    """
    Retrieve serialized classroom by ID or raise error.
    """
    classroom = get_classroom_instance_or_404(classroom_id, building)
    return ClassroomSerializer(classroom).data


def update_classroom(classroom, data: dict) -> dict:
    """
    Update a classroom instance and return serialized data.
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
    """
    Soft delete a classroom.
    """
    classroom_repository.soft_delete_classroom(classroom)


def list_classrooms_for_institution(institution) -> list[dict]:
    """
    List all classrooms for the given institution (across all buildings).
    """
    queryset = classroom_repository.list_classrooms_by_institution(institution)
    return ClassroomSerializer(queryset, many=True).data


def list_classrooms(building) -> list[dict]:
    """
    List all classrooms for a given building.
    """
    queryset = classroom_repository.list_classrooms_by_building(building)
    return ClassroomSerializer(queryset, many=True).data


from locations.repositories import classroom_repository


def get_classroom_by_id_and_institution_or_404(classroom_id: int, institution) -> dict:
    """
    Retrieve classroom by ID if it belongs to the given institution or raise error.
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


from locations.repositories import classroom_repository


def get_classroom_instance_by_institution_or_404(classroom_id: int, institution):
    """
    Retrieve classroom instance by ID and ensure it belongs to user's institution.
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
