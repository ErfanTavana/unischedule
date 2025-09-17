from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from unischedule.core.base_response import BaseResponse
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes

from schedules.services import class_session_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_class_sessions_view(request):
    institution = request.user.institution
    try:
        sessions = class_session_service.list_class_sessions(institution)
        return BaseResponse.success(
            message=SuccessCodes.CLASS_SESSION_LISTED["message"],
            code=SuccessCodes.CLASS_SESSION_LISTED["code"],
            data={"class_sessions": sessions},
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"],
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_class_session_view(request, session_id):
    institution = request.user.institution
    try:
        session = class_session_service.get_class_session_by_id_or_404(session_id, institution)
        return BaseResponse.success(
            message=SuccessCodes.CLASS_SESSION_RETRIEVED["message"],
            code=SuccessCodes.CLASS_SESSION_RETRIEVED["code"],
            data={"class_session": session},
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"],
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_class_session_view(request):
    institution = request.user.institution
    try:
        session = class_session_service.create_class_session(request.data, institution)
        return BaseResponse.success(
            message=SuccessCodes.CLASS_SESSION_CREATED["message"],
            code=SuccessCodes.CLASS_SESSION_CREATED["code"],
            data={"class_session": session},
            status_code=status.HTTP_201_CREATED,
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"],
        )
    except ValidationError as e:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=e.detail,
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.CLASS_SESSION_CREATION_FAILED["message"],
            code=ErrorCodes.CLASS_SESSION_CREATION_FAILED["code"],
            status_code=ErrorCodes.CLASS_SESSION_CREATION_FAILED["status_code"],
            errors=ErrorCodes.CLASS_SESSION_CREATION_FAILED["errors"],
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_class_session_view(request, session_id):
    institution = request.user.institution
    try:
        session = class_session_service.get_class_session_instance_or_404(session_id, institution)
        updated = class_session_service.update_class_session(session, request.data)
        return BaseResponse.success(
            message=SuccessCodes.CLASS_SESSION_UPDATED["message"],
            code=SuccessCodes.CLASS_SESSION_UPDATED["code"],
            data={"class_session": updated},
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"],
        )
    except ValidationError as e:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=e.detail,
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.CLASS_SESSION_UPDATE_FAILED["message"],
            code=ErrorCodes.CLASS_SESSION_UPDATE_FAILED["code"],
            status_code=ErrorCodes.CLASS_SESSION_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.CLASS_SESSION_UPDATE_FAILED["errors"],
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_class_session_view(request, session_id):
    institution = request.user.institution
    try:
        session = class_session_service.get_class_session_instance_or_404(session_id, institution)
        class_session_service.delete_class_session(session)
        return BaseResponse.success(
            message=SuccessCodes.CLASS_SESSION_DELETED["message"],
            code=SuccessCodes.CLASS_SESSION_DELETED["code"],
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"],
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.CLASS_SESSION_DELETION_FAILED["message"],
            code=ErrorCodes.CLASS_SESSION_DELETION_FAILED["code"],
            status_code=ErrorCodes.CLASS_SESSION_DELETION_FAILED["status_code"],
            errors=ErrorCodes.CLASS_SESSION_DELETION_FAILED["errors"],
        )
