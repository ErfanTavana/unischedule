"""Service utilities for managing semester lifecycle events per institution.

این ماژول عملیات ایجاد، به‌روزرسانی، حذف و فعال‌سازی ترم‌ها را به صورت
متمرکز مدیریت می‌کند تا invariants نظیر «یک ترم فعال» حفظ شوند.
"""

from semesters.repositories import semester_repository
from semesters.serializers.semester_serializer import (
    SemesterSerializer,
    CreateSemesterSerializer,
    UpdateSemesterSerializer,
)
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes


def list_semesters(institution):
    """Return all semesters of a given institution.

    Args:
        institution: مؤسسه‌ای که باید ترم‌های آن بازگردانده شود.

    Returns:
        list[dict]: داده‌های سریال‌شدهٔ ترم‌ها به ترتیب ذخیره شده در مخزن.
    """
    queryset = semester_repository.get_all_semesters_by_institution(institution)
    return SemesterSerializer(queryset, many=True).data


def create_semester(data, institution):
    """Create a semester for an institution and optionally activate it.

    When ``is_active`` is set in the payload the service first deactivates all
    other semesters that belong to the same institution so the new record is
    the sole active semester. This mirrors the business rule that an
    institution can only have a single active semester at any point in time.

    Args:
        data: دیکشنری داده‌های خام برای ساخت ترم.
        institution: مؤسسهٔ مالک ترم.

    Returns:
        dict: دادهٔ سریال‌شدهٔ ترم تازه ایجاد شده.
    """
    serializer = CreateSemesterSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data
    validated_data["institution"] = institution

    # If is_active=True, deactivate others
    if validated_data.get("is_active", False):
        semester_repository.deactivate_all_semesters(institution)

    semester = semester_repository.create_semester(validated_data)
    return SemesterSerializer(semester).data


def update_semester(semester, data):
    """Update a semester and propagate activation changes.

    The method applies the incoming data through ``UpdateSemesterSerializer``.
    If the update marks the semester as active, the function deactivates every
    other semester of the institution before persisting the change so the
    activation flag remains unique across the institution.

    Args:
        semester: نمونهٔ ترم موجود.
        data: داده‌های جدید برای به‌روزرسانی.

    Returns:
        dict: دادهٔ سریال‌شدهٔ ترم پس از اعمال تغییرات.
    """
    serializer = UpdateSemesterSerializer(instance=semester, data=data, partial=True)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    # If set active, deactivate others first
    if validated_data.get("is_active", False):
        semester_repository.deactivate_all_semesters(semester.institution)

    updated_semester = semester_repository.update_semester(semester, validated_data)
    return SemesterSerializer(updated_semester).data


def delete_semester(semester):
    """Soft delete a semester instance.

    Args:
        semester: نمونهٔ ترمی که باید حذف نرم شود.
    """
    return semester_repository.soft_delete_semester(semester)


def get_semester_by_id_or_404(semester_id, institution):
    """Retrieve a semester by ID for the given institution.

    Args:
        semester_id: شناسهٔ ترم مورد نظر.
        institution: مؤسسهٔ درخواست‌کننده.

    Returns:
        Semester: نمونهٔ مدل در صورت وجود.

    Raises:
        CustomValidationError: اگر ترم متعلق به مؤسسه یافت نشود.
    """
    semester = semester_repository.get_semester_by_id_and_institution(semester_id, institution)

    if not semester:
        raise CustomValidationError(
            message=ErrorCodes.SEMESTER_NOT_FOUND["message"],
            code=ErrorCodes.SEMESTER_NOT_FOUND["code"],
            status_code=ErrorCodes.SEMESTER_NOT_FOUND["status_code"],
            errors=ErrorCodes.SEMESTER_NOT_FOUND["errors"],
            data=ErrorCodes.SEMESTER_NOT_FOUND["data"],
        )
    return semester


def set_active_semester(semester):
    """Mark the provided semester as the active one for its institution.

    This helper is used by the dedicated API endpoint. It ensures all other
    semesters tied to the institution are deactivated before toggling the
    provided instance, keeping the single-active-semester invariant.

    Args:
        semester: نمونهٔ ترمی که باید فعال شود.

    Returns:
        dict: دادهٔ سریال‌شدهٔ ترم فعال پس از ذخیره.
    """
    semester_repository.deactivate_all_semesters(semester.institution)
    semester.is_active = True
    semester.save()
    return SemesterSerializer(semester).data
