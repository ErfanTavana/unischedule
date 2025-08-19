from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from accounts.services import login_user, logout_user

from unischedule.core.base_response import BaseResponse
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST - Authenticate a user using username and password. Returns token if successful.
    """
    try:
        result = login_user(request.data)
        return BaseResponse.success(
            message=SuccessCodes.LOGIN_SUCCESS["message"],
            code=SuccessCodes.LOGIN_SUCCESS["code"],
            data=result,
            status_code=status.HTTP_200_OK
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.LOGIN_FAILED["message"],
            code=ErrorCodes.LOGIN_FAILED["code"],
            status_code=ErrorCodes.LOGIN_FAILED["status_code"],
            errors=ErrorCodes.LOGIN_FAILED["errors"]
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST - Logout the authenticated user by deleting their auth token.
    """
    try:
        logout_user(request.user)
        return BaseResponse.success(
            message=SuccessCodes.LOGOUT_SUCCESS["message"],
            code=SuccessCodes.LOGOUT_SUCCESS["code"],
            data={},
            status_code=status.HTTP_200_OK
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.LOGOUT_FAILED["message"],
            code=ErrorCodes.LOGOUT_FAILED["code"],
            status_code=ErrorCodes.LOGOUT_FAILED["status_code"],
            errors=ErrorCodes.LOGOUT_FAILED["errors"]
        )
