"""Service helpers for managing building records within an institution.

توابع این فایل مسئول اعتبارسنجی داده‌ها، اجرای عملیات CRUD و برگرداندن
خطاهای یکپارچه برای معماری چندمؤسسه‌ای سامانه هستند.
"""

from locations.serializers.building_serializer import (
    CreateBuildingSerializer,
    UpdateBuildingSerializer,
    BuildingSerializer,
)
from locations.repositories import building_repository
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes


def create_building(data: dict, institution) -> dict:
    """Create a building after validating title requirements.

    The ``CreateBuildingSerializer`` ensures the title field is present and that
    it is unique for the provided institution, preventing duplicate building
    names per campus before a record is persisted.

    Args:
        data: داده‌های خام فرم شامل عنوان و توضیحات ساختمان.
        institution: مؤسسه‌ای که ساختمان به آن تعلق دارد.

    Returns:
        dict: خروجی سریال‌شدهٔ ساختمان تازه ایجاد شده.

    Raises:
        CustomValidationError: اگر اعتبارسنجی سریالایزر شکست بخورد.
    """
    serializer = CreateBuildingSerializer(data=data, context={"institution": institution})
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated_data = serializer.validated_data
    validated_data["institution"] = institution

    building = building_repository.create_building(validated_data)
    return BuildingSerializer(building).data


def get_building_instance_or_404(building_id: int, institution):
    """Fetch a building that belongs to the institution or raise an error.

    The repository call only returns buildings tied to the institution and not
    soft-deleted, so the validation guards against accessing resources outside
    the user's scope or already removed ones.

    Args:
        building_id: شناسهٔ ساختمان مورد نظر.
        institution: مؤسسهٔ درخواست‌کننده.

    Returns:
        Building: نمونهٔ مدل در صورت وجود.

    Raises:
        CustomValidationError: اگر ساختمان مطابق با مؤسسه یافت نشود.
    """
    building = building_repository.get_building_by_id_and_institution(building_id, institution)
    if not building:
        raise CustomValidationError(
            message=ErrorCodes.BUILDING_NOT_FOUND["message"],
            code=ErrorCodes.BUILDING_NOT_FOUND["code"],
            status_code=ErrorCodes.BUILDING_NOT_FOUND["status_code"],
            errors=ErrorCodes.BUILDING_NOT_FOUND["errors"],
        )
    return building


def get_building_by_id_or_404(building_id: int, institution) -> dict:
    """Return a serialized building after ownership validation.

    Reuses :func:`get_building_instance_or_404` to ensure the building exists,
    belongs to the institution and is not soft-deleted before serialization.

    Args:
        building_id: شناسهٔ ساختمان.
        institution: مؤسسهٔ مالک.

    Returns:
        dict: دادهٔ سریال‌شدهٔ ساختمان.
    """
    building = get_building_instance_or_404(building_id, institution)
    return BuildingSerializer(building).data


def update_building(building, data: dict) -> dict:
    """Apply partial updates while re-validating uniqueness constraints.

    ``UpdateBuildingSerializer`` allows partial updates but still validates that
    any new title remains unique within the same institution, preventing
    accidental duplication during edits.

    Args:
        building: نمونهٔ ساختمان موجود.
        data: داده‌های جدید برای به‌روزرسانی.

    Returns:
        dict: دادهٔ سریال‌شدهٔ ساختمان به‌روزشده.

    Raises:
        CustomValidationError: اگر سریالایزر اعتبارسنجی را رد کند.
    """
    serializer = UpdateBuildingSerializer(instance=building, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    updated_instance = serializer.save()
    return BuildingSerializer(updated_instance).data


def delete_building(building) -> None:
    """Soft delete a building after verifying it belongs to the institution.

    The instance must already pass ``get_building_instance_or_404`` so we are
    sure we do not soft delete buildings outside the caller's institution.

    Args:
        building: نمونهٔ ساختمانی که باید حذف نرم شود.
    """
    building_repository.soft_delete_building(building)


def list_buildings(institution) -> list[dict]:
    """List buildings scoped to an institution, excluding soft-deleted ones.

    The repository filters by ``is_deleted=False`` so responses only contain
    active buildings visible to the institution.

    Args:
        institution: مؤسسهٔ مالک ساختمان‌ها.

    Returns:
        list[dict]: لیست داده‌های سریال‌شدهٔ ساختمان‌ها.
    """
    queryset = building_repository.list_buildings_by_institution(institution)
    return BuildingSerializer(queryset, many=True).data
