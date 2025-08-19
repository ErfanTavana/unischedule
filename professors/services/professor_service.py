from django.db import IntegrityError
from rest_framework import serializers

from unischedule.core.exceptions import CustomValidationError
from professors import repositories as professor_repository
from professors.serializers import (
    CreateProfessorSerializer,
    UpdateProfessorSerializer,
    ProfessorSerializer,
)
from unischedule.core.error_codes import ErrorCodes
from professors.models import Professor


def create_professor(data: dict, institution) -> dict:
    """
    Create a new professor for the given institution.
    """
    serializer = CreateProfessorSerializer(data=data, context={"institution": institution})

    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as e:
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=e.detail,
        )

    validated_data = serializer.validated_data
    validated_data["institution"] = institution

    try:
        professor = professor_repository.create_professor(validated_data)
    except IntegrityError:
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors={"national_code": ["استادی با این کد ملی وجود دارد."]},
        )

    return ProfessorSerializer(professor).data


def get_professor_instance_or_404(professor_id: int, institution) -> Professor:
    professor = professor_repository.get_professor_by_id_and_institution(
        professor_id=professor_id,
        institution=institution
    )

    if not professor:
        raise CustomValidationError(
            message=ErrorCodes.PROFESSOR_NOT_FOUND["message"],
            code=ErrorCodes.PROFESSOR_NOT_FOUND["code"],
            status_code=ErrorCodes.PROFESSOR_NOT_FOUND["status_code"],
            errors=ErrorCodes.PROFESSOR_NOT_FOUND["errors"]
        )

    return professor


def get_professor_by_id_or_404(professor_id: int, institution) -> dict:
    professor = get_professor_instance_or_404(professor_id, institution)
    return ProfessorSerializer(professor).data


def update_professor(professor, data: dict) -> dict:
    """
    Update an existing professor and return serialized data.
    """
    serializer = UpdateProfessorSerializer(instance=professor, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    updated_instance = serializer.save()
    return ProfessorSerializer(updated_instance).data


def delete_professor(professor) -> None:
    """
    Soft delete a professor.
    """
    professor_repository.soft_delete_professor(professor)


def list_professors(institution) -> list[dict]:
    """
    List all professors for an institution.
    """
    queryset = professor_repository.list_professors_by_institution(institution)
    return ProfessorSerializer(queryset, many=True).data
