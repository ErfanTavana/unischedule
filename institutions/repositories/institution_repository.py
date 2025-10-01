from typing import Iterable

from institutions.models import Institution


def create_institution(data: dict) -> Institution:
    """Persist a new institution instance using validated data."""

    return Institution.objects.create(**data)


def get_institution_by_id(institution_id: int) -> Institution | None:
    # Returns: single ``Institution`` instance (or ``None``) filtered by primary key on active records.
    return Institution.objects.filter(id=institution_id).first()


def get_institution_by_slug(slug: str) -> Institution | None:
    # Returns: ``Institution`` (or ``None``) where the slug matches and ``is_deleted=False`` via the default manager.
    return Institution.objects.filter(slug=slug).first()


def list_institutions() -> Iterable[Institution]:
    # Returns: ordered queryset of active institutions (``is_deleted=False``) sorted by newest first.
    return Institution.objects.all().order_by("-created_at")


def update_institution_fields(institution: Institution, fields: dict) -> Institution:
    """Apply a dict of field updates to the provided institution and save it."""

    for field, value in fields.items():
        setattr(institution, field, value)
    institution.save()
    return institution


def soft_delete_institution(institution: Institution) -> None:
    """Perform a soft delete using the base model's custom behaviour."""

    institution.delete()
