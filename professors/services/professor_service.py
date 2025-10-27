"""Service helpers that encapsulate professor CRUD workflows.

این ماژول منطق دامنه‌ای ساخت، به‌روزرسانی، لیست و حذف استادان را متمرکز
می‌کند تا viewها تنها وظیفهٔ مدیریت درخواست و پاسخ را بر عهده داشته باشند.
هر تابع وظیفهٔ اعتبارسنجی داده‌ها، فراخوانی مخازن و تولید خطاهای
``CustomValidationError`` با جزئیات ساخت‌یافته را بر عهده دارد.
"""

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
    """Create a new professor belonging to the given institution.

    Args:
        data: دیکشنری داده‌های خام شامل اطلاعات هویتی استاد.
        institution: مؤسسه‌ای که استاد باید به آن نسبت داده شود.

    Returns:
        dict: خروجی سریال‌شدهٔ استاد تازه ایجاد شده.

    Raises:
        CustomValidationError: اگر اعتبارسنجی شکست بخورد یا کد ملی تکراری باشد.
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

    # We still guard against race conditions at the database level to prevent
    # creating professors with duplicate national codes inside the same
    # institution even if the serializer validation passes.
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
    """Return a professor instance or raise a not found error.

    Args:
        professor_id: شناسهٔ استاد مورد نظر.
        institution: مؤسسه‌ای که استاد باید به آن تعلق داشته باشد.

    Returns:
        Professor: نمونهٔ مدل در صورت وجود.

    Raises:
        CustomValidationError: اگر استاد پیدا نشود یا به مؤسسه تعلق نداشته باشد.
    """
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
    """Return serialized professor data for the given identifier.

    Args:
        professor_id: شناسهٔ استاد هدف.
        institution: مؤسسهٔ درخواست‌کننده.

    Returns:
        dict: دادهٔ سریال‌شدهٔ استاد.

    Raises:
        CustomValidationError: همان خطای ``get_professor_instance_or_404`` در صورت فقدان.
    """
    professor = get_professor_instance_or_404(professor_id, institution)
    return ProfessorSerializer(professor).data


def update_professor(professor, data: dict) -> dict:
    """Update an existing professor instance and return serialized data.

    Args:
        professor: نمونهٔ مدل که باید ویرایش شود.
        data: داده‌های جدید (می‌تواند جزئی باشد).

    Returns:
        dict: خروجی سریال‌شدهٔ استاد بعد از اعمال تغییرات.

    Raises:
        CustomValidationError: اگر سریالایزر اعتبارسنجی را رد کند.
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
    """Soft delete the provided professor instance.

    Args:
        professor: نمونهٔ استادی که باید به صورت نرم حذف شود.
    """
    professor_repository.soft_delete_professor(professor)


def list_professors(institution) -> list[dict]:
    """Return serialized data for all professors of the institution.

    Args:
        institution: مؤسسه‌ای که باید فهرست استادان آن بازگردانده شود.

    Returns:
        list[dict]: مجموعه‌ای از داده‌های سریال‌شدهٔ استادان فعال.
    """
    queryset = professor_repository.list_professors_by_institution(institution)
    return ProfessorSerializer(queryset, many=True).data
