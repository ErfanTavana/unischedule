"""Exception helpers that integrate domain errors with DRF's machinery.

The module centralises a single custom exception to standardise how service
layer validations bubble up to API responses. It mirrors the payload format
produced by :class:`unischedule.core.base_response.BaseResponse` so clients see
consistent structures whether the error was raised manually or via helper
functions.
"""

from rest_framework.exceptions import APIException
from rest_framework import status


class CustomValidationError(APIException):
    """Raise domain-specific validation errors that follow the API contract."""

    def __init__(
        self,
        message="An error occurred.",
        code=2000,
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
        data=None
    ):
        """Initialise the exception with API-friendly fields.

        Args:
            message (str): Main error message for client.
            code (int | str): Logical error code used in API (e.g., ``"3001"``).
            errors (list | dict): Validation errors or extra error info.
            status_code (int): HTTP status code (e.g., 400, 403).
            data (dict): Optional additional data to return to the client.
        """
        self.status_code = status_code
        self.detail = {
            "success": False,
            "message": message,
            "code": code,
            "errors": errors or [],
            "data": data or {}
        }
