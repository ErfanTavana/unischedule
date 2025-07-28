from rest_framework.exceptions import APIException
from rest_framework import status


class CustomValidationError(APIException):
    """
    Custom exception for handling logical or validation-related errors in service layer.

    This is used in cases like "OTP not expired", "duplicate semester", etc., and fully integrates with DRF's exception system.
    """

    def __init__(
        self,
        message="An error occurred.",
        code=2000,
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
        data=None
    ):
        """
        Args:
            message (str): Main error message for client
            code (int or str): Logical error code used in API (e.g., "3001")
            errors (list or dict): Validation errors or extra error info
            status_code (int): HTTP status code (e.g., 400, 403)
            data (dict): Optional additional data to return to the client
        """
        self.status_code = status_code
        self.detail = {
            "success": False,
            "message": message,
            "code": code,
            "errors": errors or [],
            "data": data or {}
        }
