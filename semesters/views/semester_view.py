from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from unischedule.core.base_response import BaseResponse
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes

from semesters.services import semester_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_semesters_view(request):
    """Handle ``GET`` requests by delegating to the service layer.

    The view resolves the current user's institution, fetches all related
    semesters through ``semester_service.list_semesters`` and wraps the result
    in the unified ``BaseResponse`` envelope. No exceptional branches are
    expected here because the service simply returns an empty list when the
    institution has no semesters.
    """
    institution = request.user.institution
    semesters = semester_service.list_semesters(institution)

    return BaseResponse.success(
        message=SuccessCodes.SEMESTER_LISTED["message"],
        code=SuccessCodes.SEMESTER_LISTED["code"],
        data={"semesters": semesters}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_semester_view(request):
    """Create a new semester for the authenticated user's institution.

    The view pulls the request payload and forwards it to the service layer.
    Domain errors raised as ``CustomValidationError`` (e.g. duplicates) and
    serializer ``ValidationError`` are mapped to the standard error response
    payloads, while any unforeseen exception is converted into a generic
    ``SEMESTER_CREATION_FAILED`` message. Successful requests return the
    serialized semester with a ``201`` status code.
    """
    institution = request.user.institution
    data = request.data

    try:
        semester = semester_service.create_semester(data, institution)
        return BaseResponse.success(
            message=SuccessCodes.SEMESTER_CREATED["message"],
            code=SuccessCodes.SEMESTER_CREATED["code"],
            data={"semester": semester},
            status_code=status.HTTP_201_CREATED
        )
    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except ValidationError as e:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=e.detail
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.SEMESTER_CREATION_FAILED["message"],
            code=ErrorCodes.SEMESTER_CREATION_FAILED["code"],
            status_code=ErrorCodes.SEMESTER_CREATION_FAILED["status_code"],
            errors=ErrorCodes.SEMESTER_CREATION_FAILED["errors"]
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_semester_view(request, semester_id):
    """Update an existing semester after ensuring it belongs to the user.

    The view first resolves the semester via ``get_semester_by_id_or_404`` to
    guarantee ownership. Afterwards it attempts the update and responds with a
    success payload. The three ``except`` blocks translate domain errors,
    serializer validation issues and unexpected exceptions into consistent API
    responses so clients always receive a structured message.
    """
    institution = request.user.institution
    semester = semester_service.get_semester_by_id_or_404(semester_id, institution)

    try:
        updated_semester = semester_service.update_semester(semester, request.data)
        return BaseResponse.success(
            message=SuccessCodes.SEMESTER_UPDATED["message"],
            code=SuccessCodes.SEMESTER_UPDATED["code"],
            data={"semester": updated_semester}
        )

    except CustomValidationError as e:
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except ValidationError as e:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=e.detail
        )

    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.SEMESTER_UPDATE_FAILED["message"],
            code=ErrorCodes.SEMESTER_UPDATE_FAILED["code"],
            status_code=ErrorCodes.SEMESTER_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.SEMESTER_UPDATE_FAILED["errors"]
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_semester_view(request, semester_id):
    """Soft delete a semester that belongs to the authenticated institution.

    After resolving the semester via the shared helper the view calls the
    service layer to perform the soft delete, then returns a standard success
    message. No additional exception handling is required because the helper
    already raises the structured not-found error if needed.
    """
    institution = request.user.institution
    semester = semester_service.get_semester_by_id_or_404(semester_id, institution)
    semester_service.delete_semester(semester)

    return BaseResponse.success(
        message=SuccessCodes.SEMESTER_DELETED["message"],
        code=SuccessCodes.SEMESTER_DELETED["code"]
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_active_semester_view(request, semester_id):
    """Mark the target semester as active for the institution.

    The view shares the lookup helper used by other actions, then delegates to
    ``semester_service.set_active_semester`` which handles deactivating any
    previously active record. The updated semester is returned in a standard
    success envelope.
    """
    institution = request.user.institution
    semester = semester_service.get_semester_by_id_or_404(semester_id, institution)

    updated = semester_service.set_active_semester(semester)

    return BaseResponse.success(
        message=SuccessCodes.SEMESTER_SET_ACTIVE["message"],
        code=SuccessCodes.SEMESTER_SET_ACTIVE["code"],
        data={"semester": updated}
    )
