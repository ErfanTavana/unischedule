from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from unischedule.core.base_response import BaseResponse
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes

from courses.services import course_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_courses_view(request):
    """
    GET - List all courses for the authenticated user's institution.
    """
    institution = request.user.institution
    courses = course_service.list_courses(institution)

    return BaseResponse.success(
        message=SuccessCodes.COURSE_LISTED["message"],
        code=SuccessCodes.COURSE_LISTED["code"],
        data={"courses": courses}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_course_view(request, course_id):
    """
    GET - Retrieve a course by ID.
    """
    institution = request.user.institution
    course = course_service.get_course_by_id_or_404(course_id, institution)

    return BaseResponse.success(
        message=SuccessCodes.COURSE_RETRIEVED["message"],
        code=SuccessCodes.COURSE_RETRIEVED["code"],
        data={"course": course}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_course_view(request):
    """
    POST - Create a new course.
    """
    institution = request.user.institution
    data = request.data

    try:
        course = course_service.create_course(data, institution)
        return BaseResponse.success(
            message=SuccessCodes.COURSE_CREATED["message"],
            code=SuccessCodes.COURSE_CREATED["code"],
            data={"course": course},
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
            message=ErrorCodes.COURSE_CREATION_FAILED["message"],
            code=ErrorCodes.COURSE_CREATION_FAILED["code"],
            status_code=ErrorCodes.COURSE_CREATION_FAILED["status_code"],
            errors=ErrorCodes.COURSE_CREATION_FAILED["errors"]
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_course_view(request, course_id):
    """
    PUT - Update an existing course.
    """
    institution = request.user.institution
    course = course_service.get_course_instance_or_404(course_id, institution)

    try:
        updated_course = course_service.update_course(course, request.data)
        return BaseResponse.success(
            message=SuccessCodes.COURSE_UPDATED["message"],
            code=SuccessCodes.COURSE_UPDATED["code"],
            data={"course": updated_course}
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
            message=ErrorCodes.COURSE_UPDATE_FAILED["message"],
            code=ErrorCodes.COURSE_UPDATE_FAILED["code"],
            status_code=ErrorCodes.COURSE_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.COURSE_UPDATE_FAILED["errors"]
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_course_view(request, course_id):
    """
    DELETE - Soft delete a course.
    """
    institution = request.user.institution
    course = course_service.get_course_instance_or_404(course_id, institution)

    try:
        course_service.delete_course(course)
        return BaseResponse.success(
            message=SuccessCodes.COURSE_DELETED["message"],
            code=SuccessCodes.COURSE_DELETED["code"]
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.COURSE_DELETION_FAILED["message"],
            code=ErrorCodes.COURSE_DELETION_FAILED["code"],
            status_code=ErrorCodes.COURSE_DELETION_FAILED["status_code"],
            errors=ErrorCodes.COURSE_DELETION_FAILED["errors"]
        )
