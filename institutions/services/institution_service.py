"""High-level operations for managing institutions and their media assets.

The helpers in this module coordinate serializer validation, repository
queries, and cache invalidation to keep the view layer minimal. They provide
comprehensive error reporting through :class:`CustomValidationError` so API
responses remain consistent across the project.
"""

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
    """Validate that an institution instance is present.

    Args:
        institution: نمونه‌ای از مدل مؤسسه که انتظار می‌رود خالی نباشد.

    Raises:
        CustomValidationError: اگر مقدار ورودی تهی باشد تا درخواست‌کننده از نبود
        دسترسی یا مقدار مطلع شود.
    """
    if not institution:
        raise CustomValidationError(
            message=ErrorCodes.INSTITUTION_REQUIRED["message"],
            code=ErrorCodes.INSTITUTION_REQUIRED["code"],
            status_code=ErrorCodes.INSTITUTION_REQUIRED["status_code"],
            errors=ErrorCodes.INSTITUTION_REQUIRED["errors"],
            data=ErrorCodes.INSTITUTION_REQUIRED["data"],
        )


def _invalidate_display_caches(institution) -> None:
    """Invalidate cached display payloads for screens owned by the institution.

    Args:
        institution: مؤسسه‌ای که صفحه‌نمایش‌های وابسته به آن باید ریفرش شوند.

    Notes:
        این تابع واردات تنبل انجام می‌دهد تا از حلقه‌های وابستگی جلوگیری کند و
        سپس کش هر نمایش فعال را پاک می‌کند تا تغییر لوگو یا مشخصات مؤسسه در
        لحظه منعکس شود.
    """
    from displays.repositories import display_screen_repository
    from displays.services import display_service

    screens = display_screen_repository.list_active_display_screens_by_institution(institution)
    for screen in screens:
        display_service.invalidate_screen_cache(screen)


def list_institutions() -> list[dict]:
    """Return serialized data for all active institutions.

    Returns:
        list[dict]: مجموعه‌ای از دیکشنری‌ها که توسط ``InstitutionSerializer``
        ساخته شده و برای پاسخ‌های API آماده هستند.
    """

    queryset = institution_repository.list_institutions()
    return InstitutionSerializer(queryset, many=True).data


def create_institution(data: dict) -> dict:
    """Create a new institution after validating input data.

    Args:
        data: دیکشنری داده‌های خام که معمولاً از بدنهٔ درخواست API دریافت می‌شود.

    Returns:
        dict: خروجی سریال‌شدهٔ مؤسسهٔ تازه ایجاد شده.

    Raises:
        CustomValidationError: در صورت شکست اعتبارسنجی سریالایزر یا وجود اسلاگ
        تکراری برای مؤسسهٔ فعال دیگری.
    """

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
    """Return an institution instance or raise a structured not-found error.

    Args:
        institution_id: شناسهٔ عددی مؤسسهٔ مورد نظر.

    Returns:
        institutions.models.Institution: نمونهٔ بازیابی شده از پایگاه داده.

    Raises:
        CustomValidationError: اگر مؤسسه‌ای با شناسه و وضعیت فعال یافت نشود.
    """

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
    """Serialize a single institution by ID, raising an error when missing.

    Args:
        institution_id: شناسهٔ مؤسسه‌ای که باید واکشی شود.

    Returns:
        dict: دادهٔ سریال‌شدهٔ مؤسسه برای مصرف در پاسخ API.

    Raises:
        CustomValidationError: اگر مؤسسه‌ای با شناسهٔ ورودی وجود نداشته باشد.
    """

    institution = get_institution_instance_or_404(institution_id)
    return InstitutionSerializer(institution).data


def update_institution(institution, data: dict) -> dict:
    """Update an institution instance with a validated payload.

    Args:
        institution: نمونهٔ مؤسسه که باید ویرایش شود.
        data: دیکشنری داده‌های جدید که می‌تواند بخشی از فیلدها را شامل شود.

    Returns:
        dict: خروجی سریال‌شدهٔ مؤسسه پس از ذخیرهٔ تغییرات.

    Raises:
        CustomValidationError: اگر اعتبارسنجی شکست بخورد یا اسلاگ جدید با مؤسسهٔ
        فعال دیگری در تضاد باشد.
    """

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
    """Soft delete the provided institution instance.

    Args:
        institution: نمونهٔ مؤسسه‌ای که باید حذف نرم شود.

    Raises:
        CustomValidationError: در صورت بروز خطا در لایهٔ مخزن که مانع حذف می‌شود.
    """

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
    """Return the serialized logo metadata for the provided institution.

    Args:
        institution: نمونهٔ مؤسسه‌ای که قرار است لوگوی آن خوانده شود.
        context: تنظیمات اضافی برای سریالایزر لوگو.

    Returns:
        dict: متادیتای لوگوی مؤسسه شامل آدرس و ابعاد در صورت وجود.

    Raises:
        CustomValidationError: اگر مؤسسه ارائه نشده باشد.
    """

    _ensure_institution(institution)
    serializer = InstitutionLogoSerializer(institution, context=context or {})
    return serializer.data


def update_institution_logo(institution, data: dict, *, context: dict | None = None) -> dict:
    """Update the institution logo with a new file payload.

    Args:
        institution: مؤسسه‌ای که لوگوی آن باید تغییر کند.
        data: دیکشنری شامل فایل و متادیتای لوگو.
        context: تنظیمات اختیاری سریالایزر، مانند درخواست فعلی.

    Returns:
        dict: متادیتای لوگوی جدید پس از ذخیره‌سازی و پاکسازی کش‌های مرتبط.

    Raises:
        CustomValidationError: در صورت نبود مؤسسه یا شکست اعتبارسنجی سریالایزر.
    """

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
    """Remove the stored logo from the institution profile.

    Args:
        institution: نمونهٔ مؤسسه‌ای که باید لوگوی آن حذف شود.
        context: تنظیمات اختیاری سریالایزر برای شکل‌دهی خروجی.

    Returns:
        dict: متادیتای به‌روز شدهٔ لوگو پس از حذف (معمولاً مقادیر تهی).

    Raises:
        CustomValidationError: اگر مؤسسه ارائه نشود.
    """

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
