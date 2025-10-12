from django.contrib.auth import authenticate
from accounts.repositories import (
    delete_token,
    get_or_create_token_by_user,
    get_token_by_user,
)
from accounts.serializers import LoginSerializer, ChangePasswordSerializer
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes


def login_user(data: dict) -> dict:
    """Authenticate a user and return an API token payload.

    Args:
        data: Raw credential payload expected to contain ``username`` and
            ``password`` fields provided by the request body.

    Returns:
        dict: A dictionary containing the issued token and a subset of the
            user's profile information that should be returned to the client.

    Raises:
        CustomValidationError: Raised when serializer validation fails or when
            the provided credentials do not match any active user.
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
    token = get_or_create_token_by_user(user)

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
    """Invalidate an authenticated user's session token.

    Args:
        user: The authenticated ``User`` instance whose token must be removed.

    Raises:
        CustomValidationError: Raised when the user does not currently possess
            a token, indicating that the logout request is invalid.
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
    """Validate and update the authenticated user's password.

    Args:
        user: The authenticated ``User`` instance requesting the change.
        data: Request payload containing the current password and the desired
            new password information.

    Raises:
        CustomValidationError: Raised when any validation step fails, including
            serializer validation, incorrect current password, or policy
            violations enforced by Django's password validators.
    """
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
