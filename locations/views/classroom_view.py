from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from unischedule.core.base_response import BaseResponse
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes

from locations.services import classroom_service, building_service
from locations.services import get_building_instance_or_404


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_all_classrooms_view(request):
    """
    GET - List all classrooms for the authenticated user's institution (across all buildings).
    """
    institution = request.user.institution
    classrooms = classroom_service.list_classrooms_for_institution(institution)

    return BaseResponse.success(
        message=SuccessCodes.CLASSROOM_LISTED["message"],
        code=SuccessCodes.CLASSROOM_LISTED["code"],
        data={"classrooms": classrooms}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_classrooms_view(request, building_id):
    institution = request.user.institution

    building = get_building_instance_or_404(building_id, institution)

    classrooms = classroom_service.list_classrooms(building)

    return BaseResponse.success(
        message=SuccessCodes.CLASSROOM_LISTED["message"],
        code=SuccessCodes.CLASSROOM_LISTED["code"],
        data={"classrooms": classrooms}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_classroom_view(request, classroom_id):
    """
    GET - Retrieve a classroom by its ID if it belongs to the user's institution.
    """
    institution = request.user.institution
    classroom = classroom_service.get_classroom_by_id_and_institution_or_404(classroom_id, institution)

    return BaseResponse.success(
        message=SuccessCodes.CLASSROOM_RETRIEVED["message"],
        code=SuccessCodes.CLASSROOM_RETRIEVED["code"],
        data={"classroom": classroom}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_classroom_view(request, building_id):
    """
    POST - Create a new classroom under a specific building.
    """
    institution = request.user.institution
    building = building_service.get_building_instance_or_404(building_id, institution)
    data = request.data

    try:
        classroom = classroom_service.create_classroom(data, building)
        return BaseResponse.success(
            message=SuccessCodes.CLASSROOM_CREATED["message"],
            code=SuccessCodes.CLASSROOM_CREATED["code"],
            data={"classroom": classroom},
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
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.CLASSROOM_CREATION_FAILED["message"],
            code=ErrorCodes.CLASSROOM_CREATION_FAILED["code"],
            status_code=ErrorCodes.CLASSROOM_CREATION_FAILED["status_code"],
            errors=ErrorCodes.CLASSROOM_CREATION_FAILED["errors"]
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_classroom_view(request, classroom_id):
    """
    PUT - Update an existing classroom by its ID (only if it belongs to the user's institution).
    """
    institution = request.user.institution

    try:
        # Ensure the classroom belongs to the same institution
        classroom = classroom_service.get_classroom_instance_by_institution_or_404(
            classroom_id=classroom_id,
            institution=institution
        )

        updated_classroom = classroom_service.update_classroom(classroom, request.data)

        return BaseResponse.success(
            message=SuccessCodes.CLASSROOM_UPDATED["message"],
            code=SuccessCodes.CLASSROOM_UPDATED["code"],
            data={"classroom": updated_classroom}
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
            message=ErrorCodes.CLASSROOM_UPDATE_FAILED["message"],
            code=ErrorCodes.CLASSROOM_UPDATE_FAILED["code"],
            status_code=ErrorCodes.CLASSROOM_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.CLASSROOM_UPDATE_FAILED["errors"]
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_classroom_view(request, classroom_id):
    """
    DELETE - Soft delete a classroom if it belongs to the authenticated user's institution.
    """
    institution = request.user.institution

    try:
        # ensure classroom belongs to the same institution
        classroom = classroom_service.get_classroom_instance_by_institution_or_404(
            classroom_id=classroom_id,
            institution=institution
        )

        classroom_service.delete_classroom(classroom)

        return BaseResponse.success(
            message=SuccessCodes.CLASSROOM_DELETED["message"],
            code=SuccessCodes.CLASSROOM_DELETED["code"]
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
            message=ErrorCodes.CLASSROOM_DELETION_FAILED["message"],
            code=ErrorCodes.CLASSROOM_DELETION_FAILED["code"],
            status_code=ErrorCodes.CLASSROOM_DELETION_FAILED["status_code"],
            errors=ErrorCodes.CLASSROOM_DELETION_FAILED["errors"]
        )
