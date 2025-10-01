from locations.models import Classroom, Building
from institutions.models import Institution

def create_classroom(data: dict) -> Classroom:
    """Create a classroom using ``objects.create`` for a single INSERT.

    ``create`` is efficient here because the service layer already validated the
    payload, allowing Django to execute one insert query without additional
    lookups.
    """
    return Classroom.objects.create(**data)


def get_classroom_by_id_and_building(classroom_id: int, building: Building) -> Classroom | None:
    """Return a classroom tied to a building via ``filter(...).first()``.

    Filtering by building and ``is_deleted=False`` ensures we only surface active
    rooms that belong to the expected parent without throwing exceptions.
    """
    return Classroom.objects.filter(
        id=classroom_id,
        building=building,
        is_deleted=False
    ).first()


def list_classrooms_by_institution(institution: Institution) -> list[Classroom]:
    """List active classrooms for an institution ordered by creation date.

    The ``filter`` with ``order_by('-created_at')`` performs a single query that
    scopes classrooms through ``building__institution`` while excluding
    soft-deleted entries.
    """
    return Classroom.objects.filter(
        building__institution=institution,
        is_deleted=False
    ).order_by("-created_at")


def list_classrooms_by_building(building: Building) -> list[Classroom]:
    """List classrooms for a building using ``filter`` and ``order_by``.

    This yields the active classrooms sorted by ``created_at`` descending so UI
    consumers can display the latest additions first.
    """
    return Classroom.objects.filter(
        building=building,
        is_deleted=False
    ).order_by("-created_at")


def update_classroom_fields(classroom: Classroom, fields: dict) -> Classroom:
    """Manually mutate fields on the instance before calling ``save``.

    Consolidates updates into a single ``UPDATE`` query executed when
    ``save`` runs after all field assignments.
    """
    for key, value in fields.items():
        setattr(classroom, key, value)
    classroom.save()
    return classroom


def soft_delete_classroom(classroom: Classroom) -> None:
    """Soft delete a classroom by toggling ``is_deleted`` then saving.

    This keeps the soft-delete policy centralized: a single ``UPDATE`` statement
    marks the record hidden from future queries while preserving history.
    """
    classroom.is_deleted = True
    classroom.save()


def get_classroom_by_id_and_institution(classroom_id: int, institution) -> Classroom | None:
    """Fetch a classroom limited by institution ownership via ``filter``.

    The chained lookup uses joins on ``building__institution`` while excluding
    soft-deleted rows, giving a safe ``SELECT`` that returns ``None`` when not
    found instead of raising exceptions.
    """
    return Classroom.objects.filter(
        id=classroom_id,
        is_deleted=False,
        building__institution=institution
    ).first()
