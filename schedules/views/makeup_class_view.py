from __future__ import annotations

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from unischedule.core.base_response import BaseResponse
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes

from schedules.services import class_adjustment_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_makeup_class_sessions_view(request):
    """لیست جلسات جبرانی مؤسسهٔ کاربر را همراه با مدیریت خطا برمی‌گرداند."""

    institution = request.user.institution
    try:
        makeups = class_adjustment_service.list_makeup_class_sessions(institution)
        return BaseResponse.success(
            message=SuccessCodes.MAKEUP_SESSION_LISTED["message"],
            code=SuccessCodes.MAKEUP_SESSION_LISTED["code"],
            data={"makeup_sessions": makeups},
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_makeup_class_session_view(request):
    """جلسهٔ جبرانی جدید ایجاد کرده و پاسخ استاندارد موفقیت یا خطا تولید می‌کند."""

    institution = request.user.institution
    try:
        makeup = class_adjustment_service.create_makeup_class_session(
            request.data, institution
        )
        return BaseResponse.success(
            message=SuccessCodes.MAKEUP_SESSION_CREATED["message"],
            code=SuccessCodes.MAKEUP_SESSION_CREATED["code"],
            data={"makeup_session": makeup},
            status_code=status.HTTP_201_CREATED,
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )
    except ValidationError as exc:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=exc.detail,
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.MAKEUP_SESSION_CREATION_FAILED["message"],
            code=ErrorCodes.MAKEUP_SESSION_CREATION_FAILED["code"],
            status_code=ErrorCodes.MAKEUP_SESSION_CREATION_FAILED["status_code"],
            errors=ErrorCodes.MAKEUP_SESSION_CREATION_FAILED["errors"],
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_makeup_class_session_view(request, makeup_id: int):
    """جزئیات جلسهٔ جبرانی مشخص را در قالب BaseResponse بازمی‌گرداند."""

    institution = request.user.institution
    try:
        makeup = class_adjustment_service.get_makeup_class_session_by_id_or_404(
            makeup_id, institution
        )
        return BaseResponse.success(
            message=SuccessCodes.MAKEUP_SESSION_RETRIEVED["message"],
            code=SuccessCodes.MAKEUP_SESSION_RETRIEVED["code"],
            data={"makeup_session": makeup},
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_makeup_class_session_view(request, makeup_id: int):
    """جلسهٔ جبرانی موجود را به‌روزرسانی کرده و استثناها را به خطاهای سراسری تبدیل می‌کند."""

    institution = request.user.institution
    try:
        makeup_instance = class_adjustment_service.get_makeup_class_session_instance_or_404(
            makeup_id, institution
        )
        updated = class_adjustment_service.update_makeup_class_session(
            makeup_instance, request.data
        )
        return BaseResponse.success(
            message=SuccessCodes.MAKEUP_SESSION_UPDATED["message"],
            code=SuccessCodes.MAKEUP_SESSION_UPDATED["code"],
            data={"makeup_session": updated},
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )
    except ValidationError as exc:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=exc.detail,
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.MAKEUP_SESSION_UPDATE_FAILED["message"],
            code=ErrorCodes.MAKEUP_SESSION_UPDATE_FAILED["code"],
            status_code=ErrorCodes.MAKEUP_SESSION_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.MAKEUP_SESSION_UPDATE_FAILED["errors"],
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_makeup_class_session_view(request, makeup_id: int):
    """جلسهٔ جبرانی را حذف نرم کرده و وضعیت موفق یا خطا را بازتاب می‌دهد."""

    institution = request.user.institution
    try:
        makeup_instance = class_adjustment_service.get_makeup_class_session_instance_or_404(
            makeup_id, institution
        )
        class_adjustment_service.delete_makeup_class_session(makeup_instance)
        return BaseResponse.success(
            message=SuccessCodes.MAKEUP_SESSION_DELETED["message"],
            code=SuccessCodes.MAKEUP_SESSION_DELETED["code"],
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.MAKEUP_SESSION_DELETION_FAILED["message"],
            code=ErrorCodes.MAKEUP_SESSION_DELETION_FAILED["code"],
            status_code=ErrorCodes.MAKEUP_SESSION_DELETION_FAILED["status_code"],
            errors=ErrorCodes.MAKEUP_SESSION_DELETION_FAILED["errors"],
        )
