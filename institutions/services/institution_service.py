from institutions import repositories as institution_repository
from institutions.serializers import (
    InstitutionSerializer,
    CreateInstitutionSerializer,
    UpdateInstitutionSerializer,
)
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError


def list_institutions() -> list[dict]:
    """Return serialized data for all active institutions."""

    queryset = institution_repository.list_institutions()
    return InstitutionSerializer(queryset, many=True).data


def create_institution(data: dict) -> dict:
    """Create a new institution after validating input data."""

    serializer = CreateInstitutionSerializer(data=data)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated = serializer.validated_data

    # Prevent duplicate slugs by verifying the slug does not belong to another active institution.
    slug = validated["slug"]
    if institution_repository.get_institution_by_slug(slug):
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["message"],
            code=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["code"],
            status_code=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["status_code"],
            errors=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["errors"],
        )

    institution = institution_repository.create_institution(validated)
    return InstitutionSerializer(institution).data


def get_institution_instance_or_404(institution_id: int):
    """Return an institution instance or raise a structured not-found error."""

    institution = institution_repository.get_institution_by_id(institution_id)
    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_NOT_FOUND["message"],
            code=ErrorCodes.INSTITUTION_NOT_FOUND["code"],
            status_code=ErrorCodes.INSTITUTION_NOT_FOUND["status_code"],
            errors=ErrorCodes.INSTITUTION_NOT_FOUND["errors"],
        )
    return institution


def get_institution_by_id_or_404(institution_id: int) -> dict:
    """Serialize a single institution by ID, raising an error when missing."""

    institution = get_institution_instance_or_404(institution_id)
    return InstitutionSerializer(institution).data


def update_institution(institution, data: dict) -> dict:
    """Update an institution instance with validated payload."""

    serializer = UpdateInstitutionSerializer(instance=institution, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated = serializer.validated_data

    # Ensure slug changes do not collide with another active institution.
    slug = validated.get("slug")
    if slug:
        existing = institution_repository.get_institution_by_slug(slug)
        if existing and existing.id != institution.id:
            raise CustomValidationError(
                message=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["message"],
                code=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["code"],
                status_code=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["status_code"],
                errors=ErrorCodes.INSTITUTION_DUPLICATE_SLUG["errors"],
            )

    updated = serializer.save()
    return InstitutionSerializer(updated).data


def delete_institution(institution) -> None:
    """Soft delete the provided institution instance."""

    try:
        institution_repository.soft_delete_institution(institution)
    except Exception as exc:  # pragma: no cover - defensive programming
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_DELETION_FAILED["message"],
            code=ErrorCodes.INSTITUTION_DELETION_FAILED["code"],
            status_code=ErrorCodes.INSTITUTION_DELETION_FAILED["status_code"],
            errors=[str(exc)],
        )
