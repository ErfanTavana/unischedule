from locations.serializers.building_serializer import (
    CreateBuildingSerializer,
    UpdateBuildingSerializer,
    BuildingSerializer,
)
from locations.repositories import building_repository
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes


def create_building(data: dict, institution) -> dict:
    """
    Create a new building for the given institution.
    """
    serializer = CreateBuildingSerializer(data=data, context={"institution": institution})
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated_data = serializer.validated_data
    validated_data["institution"] = institution

    building = building_repository.create_building(validated_data)
    return BuildingSerializer(building).data


def get_building_instance_or_404(building_id: int, institution):
    """
    Retrieve building instance or raise 404-style error.
    """
    building = building_repository.get_building_by_id_and_institution(building_id, institution)
    if not building:
        raise CustomValidationError(
            message=ErrorCodes.BUILDING_NOT_FOUND["message"],
            code=ErrorCodes.BUILDING_NOT_FOUND["code"],
            status_code=ErrorCodes.BUILDING_NOT_FOUND["status_code"],
            errors=ErrorCodes.BUILDING_NOT_FOUND["errors"],
        )
    return building


def get_building_by_id_or_404(building_id: int, institution) -> dict:
    """
    Retrieve serialized building by ID or raise error.
    """
    building = get_building_instance_or_404(building_id, institution)
    return BuildingSerializer(building).data


def update_building(building, data: dict) -> dict:
    """
    Update a building instance and return serialized data.
    """
    serializer = UpdateBuildingSerializer(instance=building, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    updated_instance = serializer.save()
    return BuildingSerializer(updated_instance).data


def delete_building(building) -> None:
    """
    Soft delete a building.
    """
    building_repository.soft_delete_building(building)


def list_buildings(institution) -> list[dict]:
    """
    List all buildings for a given institution.
    """
    queryset = building_repository.list_buildings_by_institution(institution)
    return BuildingSerializer(queryset, many=True).data
