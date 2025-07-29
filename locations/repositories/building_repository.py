from locations.models import Building
from institutions.models import Institution


def create_building(data: dict) -> Building:
    """
    Create a new building instance.
    """
    return Building.objects.create(**data)


def get_building_by_id_and_institution(building_id: int, institution: Institution) -> Building | None:
    """
    Retrieve a building by ID and institution (if not soft-deleted).
    """
    return Building.objects.filter(id=building_id, institution=institution, is_deleted=False).first()


def list_buildings_by_institution(institution: Institution) -> list[Building]:
    """
    List all buildings for a given institution (excluding soft-deleted ones).
    """
    return Building.objects.filter(institution=institution, is_deleted=False).order_by("-created_at")


def update_building_fields(building: Building, fields: dict) -> Building:
    """
    Manually update building fields and save.
    """
    for key, value in fields.items():
        setattr(building, key, value)
    building.save()
    return building


def soft_delete_building(building: Building) -> None:
    """
    Soft delete a building (mark is_deleted = True).
    """
    building.is_deleted = True
    building.save()
