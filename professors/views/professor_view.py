from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from unischedule.core.base_response import BaseResponse
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes

from professors.services import professor_service
import logging


logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_professors_view(request):
    """GET - List all professors for the authenticated user's institution."""
    institution = request.user.institution
    professors = professor_service.list_professors(institution)

    # BaseResponse.success ensures every success response shares the same
    # envelope (message, code, data) used across the project.
    return BaseResponse.success(
        message=SuccessCodes.PROFESSOR_LISTED["message"],
        code=SuccessCodes.PROFESSOR_LISTED["code"],
        data={"professors": professors}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_professor_view(request, professor_id):
    institution = request.user.institution
    serialized_professor = professor_service.get_professor_by_id_or_404(professor_id, institution)

    # Successful retrievals are wrapped in the common response format so
    # clients can parse status metadata consistently.
    return BaseResponse.success(
        message=SuccessCodes.PROFESSOR_RETRIEVED["message"],
        code=SuccessCodes.PROFESSOR_RETRIEVED["code"],
        data={"professor": serialized_professor}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_professor_view(request):
    """
    POST - Create a new professor for the authenticated user's institution.
    """
    institution = request.user.institution
    data = request.data

    try:
        professor = professor_service.create_professor(data, institution)
        return BaseResponse.success(
            message=SuccessCodes.PROFESSOR_CREATED["message"],
            code=SuccessCodes.PROFESSOR_CREATED["code"],
            data={"professor": professor},
            status_code=status.HTTP_201_CREATED
        )

    except CustomValidationError as e:
        # Validation errors also leverage BaseResponse.error so error payloads
        # remain predictable for API consumers.
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )


    except Exception:
        # Unexpected errors fall back to a predefined error code while still
        # returning the structured error response.
        return BaseResponse.error(
            message=ErrorCodes.PROFESSOR_CREATION_FAILED["message"],
            code=ErrorCodes.PROFESSOR_CREATION_FAILED["code"],
            status_code=ErrorCodes.PROFESSOR_CREATION_FAILED["status_code"],
            errors=ErrorCodes.PROFESSOR_CREATION_FAILED["errors"]
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_professor_view(request, professor_id):
    """
    PUT - Update an existing professor.
    """
    institution = request.user.institution
    professor = professor_service.get_professor_instance_or_404(professor_id, institution)

    try:
        updated_professor_data = professor_service.update_professor(professor, request.data)
        return BaseResponse.success(
            message=SuccessCodes.PROFESSOR_UPDATED["message"],
            code=SuccessCodes.PROFESSOR_UPDATED["code"],
            data={"professor": updated_professor_data}
        )

    except CustomValidationError as e:
        # Translate domain-specific validation issues to the standard error
        # schema to keep client handling consistent.
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )

    except ValidationError as e:
        # DRF validation exceptions are also normalized via BaseResponse.
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=e.detail
        )

    except Exception:
        logger.exception("Unhandled exception while updating professor")
        # Even unexpected errors are wrapped in the same response contract.
        return BaseResponse.error(
            message=ErrorCodes.PROFESSOR_UPDATE_FAILED["message"],
            code=ErrorCodes.PROFESSOR_UPDATE_FAILED["code"],
            status_code=ErrorCodes.PROFESSOR_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.PROFESSOR_UPDATE_FAILED["errors"]
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_professor_view(request, professor_id):
    """
    DELETE - Soft delete a professor by ID.
    """
    institution = request.user.institution
    professor = professor_service.get_professor_instance_or_404(professor_id, institution)

    try:
        professor_service.delete_professor(professor)
        return BaseResponse.success(
            message=SuccessCodes.PROFESSOR_DELETED["message"],
            code=SuccessCodes.PROFESSOR_DELETED["code"]
        )
    except Exception:
        logger.exception("Unhandled exception while deleting professor")
        # Soft-delete failures are still presented through the BaseResponse
        # abstraction for a uniform API.
        return BaseResponse.error(
            message=ErrorCodes.PROFESSOR_DELETION_FAILED["message"],
            code=ErrorCodes.PROFESSOR_DELETION_FAILED["code"],
            status_code=ErrorCodes.PROFESSOR_DELETION_FAILED["status_code"],
            errors=ErrorCodes.PROFESSOR_DELETION_FAILED["errors"]
        )

