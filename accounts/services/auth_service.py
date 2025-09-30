from django.contrib.auth import authenticate
from accounts.repositories import get_token_by_user, delete_token
from accounts.serializers import LoginSerializer, ChangePasswordSerializer
from rest_framework.authtoken.models import Token
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes


def login_user(data: dict) -> dict:
    """
    Authenticate user and return token if successful.
    """
    # Validate input using LoginSerializer
    serializer = LoginSerializer(data=data)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated_data = serializer.validated_data
    username = validated_data["username"]
    password = validated_data["password"]

    # Authenticate user
    user = authenticate(username=username, password=password)
    if not user:
        raise CustomValidationError(
            message=ErrorCodes.INVALID_CREDENTIALS["message"],
            code=ErrorCodes.INVALID_CREDENTIALS["code"],
            status_code=ErrorCodes.INVALID_CREDENTIALS["status_code"],
            errors=ErrorCodes.INVALID_CREDENTIALS["errors"],
        )

    # Get or create token via repository
    token = get_token_by_user(user)
    if not token:
        token = Token.objects.create(user=user)

    return {
        "token": token.key,
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "institution_id": user.institution_id,
        }
    }


def logout_user(user) -> None:
    """
    Delete the user's auth token (logout).
    """
    token = get_token_by_user(user)
    if not token:
        raise CustomValidationError(
            message=ErrorCodes.TOKEN_NOT_FOUND["message"],
            code=ErrorCodes.TOKEN_NOT_FOUND["code"],
            status_code=ErrorCodes.TOKEN_NOT_FOUND["status_code"],
            errors=ErrorCodes.TOKEN_NOT_FOUND["errors"],
        )

    delete_token(token)


def change_user_password(user, data: dict) -> None:
    """Validate and change the authenticated user's password."""
    serializer = ChangePasswordSerializer(data=data, context={"user": user})
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated_data = serializer.validated_data
    old_password = validated_data.get("old_password")
    new_password = validated_data.get("new_password")

    if not user.check_password(old_password):
        raise CustomValidationError(
            message=ErrorCodes.PASSWORD_INCORRECT["message"],
            code=ErrorCodes.PASSWORD_INCORRECT["code"],
            status_code=ErrorCodes.PASSWORD_INCORRECT["status_code"],
            errors=ErrorCodes.PASSWORD_INCORRECT["errors"],
        )

    user.set_password(new_password)
    user.save(update_fields=["password"])
