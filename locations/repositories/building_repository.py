from locations.models import Building
from institutions.models import Institution


def create_building(data: dict) -> Building:
    """Create a new building instance using ``objects.create``.

    ``create`` is preferred here because it performs a single INSERT with the
    validated payload coming from the service layer.
    """
    return Building.objects.create(**data)


def get_building_by_id_and_institution(building_id: int, institution: Institution) -> Building | None:
    """Return the first building matching the institution using ``filter``.

    ``filter(...).first()`` expresses the lookup as a safe ``SELECT`` that also
    enforces ``is_deleted=False`` so soft-deleted buildings are excluded without
    raising ``DoesNotExist`` exceptions.
    """
    return Building.objects.filter(id=building_id, institution=institution, is_deleted=False).first()


def list_buildings_by_institution(institution: Institution) -> list[Building]:
    """Fetch active buildings for an institution ordered by recency.

    Uses ``filter`` with an ``order_by('-created_at')`` clause to deliver an
    ordered queryset, making it efficient to display the latest buildings first
    while still excluding soft-deleted rows.
    """
    return Building.objects.filter(institution=institution, is_deleted=False).order_by("-created_at")


def update_building_fields(building: Building, fields: dict) -> Building:
    """Update fields on the instance before issuing a ``save``.

    Manual attribute assignment keeps the update logic explicit while relying on
    ``save`` to perform the underlying ``UPDATE`` query once all changes are
    staged.
    """
    for key, value in fields.items():
        setattr(building, key, value)
    building.save()
    return building


def soft_delete_building(building: Building) -> None:
    """Mark the building as deleted and persist via ``save``.

    Updating ``is_deleted`` locally followed by ``save`` keeps the soft delete
    logic centralized without executing extra queries.
    """
    building.is_deleted = True
    building.save()
