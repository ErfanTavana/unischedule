from locations.models import Classroom, Building
from institutions.models import Institution

def create_classroom(data: dict) -> Classroom:
    """
    Create a new classroom with the given data.
    """
    return Classroom.objects.create(**data)


def get_classroom_by_id_and_building(classroom_id: int, building: Building) -> Classroom | None:
    """
    Retrieve a classroom by ID and building (if not soft-deleted).
    """
    return Classroom.objects.filter(
        id=classroom_id,
        building=building,
        is_deleted=False
    ).first()


def list_classrooms_by_institution(institution: Institution) -> list[Classroom]:
    """
    List all classrooms under all buildings of an institution.
    """
    return Classroom.objects.filter(
        building__institution=institution,
        is_deleted=False
    ).order_by("-created_at")


def list_classrooms_by_building(building: Building) -> list[Classroom]:
    """
    List all classrooms for a given building (excluding soft-deleted ones).
    """
    return Classroom.objects.filter(
        building=building,
        is_deleted=False
    ).order_by("-created_at")


def update_classroom_fields(classroom: Classroom, fields: dict) -> Classroom:
    """
    Update classroom fields and save.
    """
    for key, value in fields.items():
        setattr(classroom, key, value)
    classroom.save()
    return classroom


def soft_delete_classroom(classroom: Classroom) -> None:
    """
    Soft delete a classroom by setting is_deleted to True.
    """
    classroom.is_deleted = True
    classroom.save()


def get_classroom_by_id_and_institution(classroom_id: int, institution) -> Classroom | None:
    """
    Retrieve a classroom by ID and ensure it belongs to the given institution.
    """
    return Classroom.objects.filter(
        id=classroom_id,
        is_deleted=False,
        building__institution=institution
    ).first()
