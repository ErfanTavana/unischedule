from professors.models import Professor


def create_professor(data: dict) -> Professor:
    """
    Create a new professor with the given data.
    """
    return Professor.objects.create(**data)


def get_professor_by_id_and_institution(professor_id: int, institution) -> Professor | None:
    """
    Retrieve a professor by ID and institution.
    """
    return Professor.objects.filter(id=professor_id, institution=institution, is_deleted=False).first()


def list_professors_by_institution(institution) -> list[Professor]:
    """
    List all professors for a given institution (excluding soft-deleted ones).
    """
    return Professor.objects.filter(institution=institution, is_deleted=False).order_by("-created_at")


def update_professor_fields(professor: Professor, fields: dict) -> Professor:
    """
    Manually update fields and save.
    """
    for key, value in fields.items():
        setattr(professor, key, value)
    professor.save()
    return professor


def soft_delete_professor(professor: Professor) -> None:
    """
    Soft delete a professor by marking is_deleted=True.
    """
    professor.is_deleted = True
    professor.save()
