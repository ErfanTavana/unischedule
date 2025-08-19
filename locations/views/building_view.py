from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError

from unischedule.core.base_response import BaseResponse
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes
from unischedule.core.error_codes import ErrorCodes

from locations.services import building_service
import logging


logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_buildings_view(request):
    """
    GET - List all buildings for the authenticated user's institution.
    """
    institution = request.user.institution
    buildings = building_service.list_buildings(institution)

    return BaseResponse.success(
        message=SuccessCodes.BUILDING_LISTED["message"],
        code=SuccessCodes.BUILDING_LISTED["code"],
        data={"buildings": buildings}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_building_view(request, building_id):
    """
    GET - Retrieve a building by ID.
    """
    institution = request.user.institution
    building = building_service.get_building_by_id_or_404(building_id, institution)

    return BaseResponse.success(
        message=SuccessCodes.BUILDING_RETRIEVED["message"],
        code=SuccessCodes.BUILDING_RETRIEVED["code"],
        data={"building": building}
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_building_view(request):
    """
    POST - Create a new building for the authenticated user's institution.
    """
    institution = request.user.institution
    data = request.data

    try:
        building = building_service.create_building(data, institution)
        return BaseResponse.success(
            message=SuccessCodes.BUILDING_CREATED["message"],
            code=SuccessCodes.BUILDING_CREATED["code"],
            data={"building": building},
            status_code=status.HTTP_201_CREATED
        )
    except CustomValidationError as e:
        logger.exception("Validation error while creating building")
        return BaseResponse.error(
            message=e.detail["message"],
            code=e.detail["code"],
            status_code=e.status_code,
            errors=e.detail["errors"],
            data=e.detail["data"]
        )
    except Exception:
        logger.exception("Unhandled exception while creating building")
        return BaseResponse.error(
            message=ErrorCodes.BUILDING_CREATION_FAILED["message"],
            code=ErrorCodes.BUILDING_CREATION_FAILED["code"],
            status_code=ErrorCodes.BUILDING_CREATION_FAILED["status_code"],
            errors=ErrorCodes.BUILDING_CREATION_FAILED["errors"]
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_building_view(request, building_id):
    """
    PUT - Update an existing building.
    """
    institution = request.user.institution
    building = building_service.get_building_instance_or_404(building_id, institution)

    try:
        updated_building = building_service.update_building(building, request.data)
        return BaseResponse.success(
            message=SuccessCodes.BUILDING_UPDATED["message"],
            code=SuccessCodes.BUILDING_UPDATED["code"],
            data={"building": updated_building}
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
            message=ErrorCodes.BUILDING_UPDATE_FAILED["message"],
            code=ErrorCodes.BUILDING_UPDATE_FAILED["code"],
            status_code=ErrorCodes.BUILDING_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.BUILDING_UPDATE_FAILED["errors"]
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_building_view(request, building_id):
    """
    DELETE - Soft delete a building.
    """
    institution = request.user.institution
    building = building_service.get_building_instance_or_404(building_id, institution)

    try:
        building_service.delete_building(building)
        return BaseResponse.success(
            message=SuccessCodes.BUILDING_DELETED["message"],
            code=SuccessCodes.BUILDING_DELETED["code"]
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.BUILDING_DELETION_FAILED["message"],
            code=ErrorCodes.BUILDING_DELETION_FAILED["code"],
            status_code=ErrorCodes.BUILDING_DELETION_FAILED["status_code"],
            errors=ErrorCodes.BUILDING_DELETION_FAILED["errors"]
        )
