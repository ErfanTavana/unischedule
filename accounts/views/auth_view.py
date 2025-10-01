from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from accounts.services import login_user, logout_user, change_user_password

from unischedule.core.base_response import BaseResponse
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError


# Handle POST login requests from unauthenticated clients.
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    POST - Authenticate a user using username and password. Returns token if successful.
    """
    try:
        # Authenticate credentials via the service layer and package the success response.
        result = login_user(request.data)
        return BaseResponse.success(
            message=SuccessCodes.LOGIN_SUCCESS["message"],
            code=SuccessCodes.LOGIN_SUCCESS["code"],
            data=result,
            status_code=status.HTTP_200_OK
        )
    except CustomValidationError as e:
        # Surface validation errors so the client knows why authentication failed.
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except Exception:
        # Provide a generic failure response for unexpected issues during login.
        return BaseResponse.error(
            message=ErrorCodes.LOGIN_FAILED["message"],
            code=ErrorCodes.LOGIN_FAILED["code"],
            status_code=ErrorCodes.LOGIN_FAILED["status_code"],
            errors=ErrorCodes.LOGIN_FAILED["errors"]
        )


# Handle POST logout requests for authenticated users.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    POST - Logout the authenticated user by deleting their auth token.
    """
    try:
        # Remove the user's token to invalidate the current session.
        logout_user(request.user)
        return BaseResponse.success(
            message=SuccessCodes.LOGOUT_SUCCESS["message"],
            code=SuccessCodes.LOGOUT_SUCCESS["code"],
            data={},
            status_code=status.HTTP_200_OK
        )
    except CustomValidationError as e:
        # Return token related errors when the logout request is not valid.
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except Exception:
        # Catch-all for unexpected failures when attempting to logout.
        return BaseResponse.error(
            message=ErrorCodes.LOGOUT_FAILED["message"],
            code=ErrorCodes.LOGOUT_FAILED["code"],
            status_code=ErrorCodes.LOGOUT_FAILED["status_code"],
            errors=ErrorCodes.LOGOUT_FAILED["errors"]
        )


# Handle POST password change requests for authenticated users.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """POST - Change the authenticated user's password."""
    try:
        # Delegate complex password validation and update logic to the service layer.
        change_user_password(request.user, request.data)
        return BaseResponse.success(
            message=SuccessCodes.PASSWORD_CHANGE_SUCCESS["message"],
            code=SuccessCodes.PASSWORD_CHANGE_SUCCESS["code"],
            data=SuccessCodes.PASSWORD_CHANGE_SUCCESS.get("data", {}),
            status_code=status.HTTP_200_OK
        )
    except CustomValidationError as e:
        # Relay serializer or password validation errors back to the caller.
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except Exception:
        # Respond with a generic failure message for any unexpected exceptions.
        return BaseResponse.error(
            message=ErrorCodes.PASSWORD_CHANGE_FAILED["message"],
            code=ErrorCodes.PASSWORD_CHANGE_FAILED["code"],
            status_code=ErrorCodes.PASSWORD_CHANGE_FAILED["status_code"],
            errors=ErrorCodes.PASSWORD_CHANGE_FAILED["errors"]
        )
