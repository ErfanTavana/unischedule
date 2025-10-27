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
def list_class_cancellations_view(request):
    institution = request.user.institution
    try:
        cancellations = class_adjustment_service.list_class_cancellations(institution)
        return BaseResponse.success(
            message=SuccessCodes.CLASS_CANCELLATION_LISTED["message"],
            code=SuccessCodes.CLASS_CANCELLATION_LISTED["code"],
            data={"cancellations": cancellations},
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
def create_class_cancellation_view(request):
    institution = request.user.institution
    try:
        cancellation = class_adjustment_service.create_class_cancellation(
            request.data, institution
        )
        return BaseResponse.success(
            message=SuccessCodes.CLASS_CANCELLATION_CREATED["message"],
            code=SuccessCodes.CLASS_CANCELLATION_CREATED["code"],
            data={"cancellation": cancellation},
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
            message=ErrorCodes.CLASS_CANCELLATION_CREATION_FAILED["message"],
            code=ErrorCodes.CLASS_CANCELLATION_CREATION_FAILED["code"],
            status_code=ErrorCodes.CLASS_CANCELLATION_CREATION_FAILED["status_code"],
            errors=ErrorCodes.CLASS_CANCELLATION_CREATION_FAILED["errors"],
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_class_cancellation_view(request, cancellation_id: int):
    institution = request.user.institution
    try:
        cancellation = class_adjustment_service.get_class_cancellation_by_id_or_404(
            cancellation_id, institution
        )
        return BaseResponse.success(
            message=SuccessCodes.CLASS_CANCELLATION_RETRIEVED["message"],
            code=SuccessCodes.CLASS_CANCELLATION_RETRIEVED["code"],
            data={"cancellation": cancellation},
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
def update_class_cancellation_view(request, cancellation_id: int):
    institution = request.user.institution
    try:
        cancellation_instance = (
            class_adjustment_service.get_class_cancellation_instance_or_404(
                cancellation_id, institution
            )
        )
        updated = class_adjustment_service.update_class_cancellation(
            cancellation_instance, request.data
        )
        return BaseResponse.success(
            message=SuccessCodes.CLASS_CANCELLATION_UPDATED["message"],
            code=SuccessCodes.CLASS_CANCELLATION_UPDATED["code"],
            data={"cancellation": updated},
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
            message=ErrorCodes.CLASS_CANCELLATION_UPDATE_FAILED["message"],
            code=ErrorCodes.CLASS_CANCELLATION_UPDATE_FAILED["code"],
            status_code=ErrorCodes.CLASS_CANCELLATION_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.CLASS_CANCELLATION_UPDATE_FAILED["errors"],
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_class_cancellation_view(request, cancellation_id: int):
    institution = request.user.institution
    try:
        cancellation_instance = (
            class_adjustment_service.get_class_cancellation_instance_or_404(
                cancellation_id, institution
            )
        )
        class_adjustment_service.delete_class_cancellation(cancellation_instance)
        return BaseResponse.success(
            message=SuccessCodes.CLASS_CANCELLATION_DELETED["message"],
            code=SuccessCodes.CLASS_CANCELLATION_DELETED["code"],
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
            message=ErrorCodes.CLASS_CANCELLATION_DELETION_FAILED["message"],
            code=ErrorCodes.CLASS_CANCELLATION_DELETION_FAILED["code"],
            status_code=ErrorCodes.CLASS_CANCELLATION_DELETION_FAILED["status_code"],
            errors=ErrorCodes.CLASS_CANCELLATION_DELETION_FAILED["errors"],
        )
