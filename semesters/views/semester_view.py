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
    """
    GET - List all semesters for the authenticated user's institution.
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
    """
    POST - Create a new semester for the authenticated user's institution.
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
    """
    PUT - Update an existing semester.
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
    """
    DELETE - Soft delete a semester.
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
    """
    POST - Set a semester as active and deactivate all others for the same institution.
    """
    institution = request.user.institution
    semester = semester_service.get_semester_by_id_or_404(semester_id, institution)

    updated = semester_service.set_active_semester(semester)

    return BaseResponse.success(
        message=SuccessCodes.SEMESTER_SET_ACTIVE["message"],
        code=SuccessCodes.SEMESTER_SET_ACTIVE["code"],
        data={"semester": updated}
    )
