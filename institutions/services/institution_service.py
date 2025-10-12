from django.core.files.storage import default_storage

from institutions import repositories as institution_repository
from institutions.serializers import (
    InstitutionSerializer,
    CreateInstitutionSerializer,
    UpdateInstitutionSerializer,
    InstitutionLogoSerializer,
)
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError


def _ensure_institution(institution) -> None:
    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_REQUIRED["message"],
            code=ErrorCodes.INSTITUTION_REQUIRED["code"],
            status_code=ErrorCodes.INSTITUTION_REQUIRED["status_code"],
            errors=ErrorCodes.INSTITUTION_REQUIRED["errors"],
            data=ErrorCodes.INSTITUTION_REQUIRED["data"],
        )


def _invalidate_display_caches(institution) -> None:
    from displays.repositories import display_screen_repository
    from displays.services import display_service

    screens = display_screen_repository.list_active_display_screens_by_institution(institution)
    for screen in screens:
        display_service.invalidate_screen_cache(screen)


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

    previous_logo_name = institution.logo.name if getattr(institution.logo, "name", None) else None
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

    if "logo" in validated:
        new_logo_name = updated.logo.name if getattr(updated.logo, "name", None) else None
        if previous_logo_name and previous_logo_name != new_logo_name:
            try:
                default_storage.delete(previous_logo_name)
            except Exception:  # pragma: no cover - storage backend differences
                pass
        _invalidate_display_caches(updated)

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


def get_institution_logo(institution, *, context: dict | None = None) -> dict:
    """Return the serialized logo metadata for the provided institution."""

    _ensure_institution(institution)
    serializer = InstitutionLogoSerializer(institution, context=context or {})
    return serializer.data


def update_institution_logo(institution, data: dict, *, context: dict | None = None) -> dict:
    """Update the institution logo with a new file payload."""

    _ensure_institution(institution)
    serializer = InstitutionLogoSerializer(
        instance=institution,
        data=data,
        partial=True,
        context=context or {},
    )
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    previous_logo_name = institution.logo.name if getattr(institution.logo, "name", None) else None
    updated = serializer.save()
    new_logo_name = updated.logo.name if getattr(updated.logo, "name", None) else None

    if previous_logo_name and previous_logo_name != new_logo_name:
        try:
            default_storage.delete(previous_logo_name)
        except Exception:  # pragma: no cover
            pass

    _invalidate_display_caches(updated)
    return InstitutionLogoSerializer(updated, context=context or {}).data


def delete_institution_logo(institution, *, context: dict | None = None) -> dict:
    """Remove the stored logo from the institution profile."""

    _ensure_institution(institution)

    if not institution.logo:
        return InstitutionLogoSerializer(institution, context=context or {}).data

    previous_logo_name = institution.logo.name if getattr(institution.logo, "name", None) else None
    institution.logo = None
    institution.save(update_fields=["logo", "updated_at"])

    if previous_logo_name:
        try:
            default_storage.delete(previous_logo_name)
        except Exception:  # pragma: no cover
            pass

    _invalidate_display_caches(institution)
    return InstitutionLogoSerializer(institution, context=context or {}).data
