from semesters.models import Semester
from django.db.models import Q


def get_all_semesters_by_institution(institution):
    """
    Retrieve all semesters (not deleted) for a given institution, ordered by start date.
    """
    return Semester.objects.filter(institution=institution, is_deleted=False).order_by("-start_date")


def get_semester_by_id_and_institution(semester_id, institution):
    """
    Retrieve a specific semester by ID and institution.
    """
    return Semester.objects.filter(id=semester_id, institution=institution, is_deleted=False).first()


def get_active_semester(institution):
    """
    Return the currently active semester for a specific institution.
    """
    return Semester.objects.filter(institution=institution, is_active=True, is_deleted=False).first()


def create_semester(validated_data):
    """
    Create a new semester instance.
    """
    return Semester.objects.create(**validated_data)


def update_semester(instance, validated_data):
    """
    Update fields of a semester instance.
    """
    for attr, value in validated_data.items():
        setattr(instance, attr, value)
    instance.save()
    return instance


def soft_delete_semester(instance):
    """
    Soft delete a semester by setting is_deleted=True.
    """
    instance.is_deleted = True
    instance.save()
    return instance


def deactivate_all_semesters(institution):
    """
    Deactivate all semesters of a given institution.
    """
    Semester.objects.filter(institution=institution, is_deleted=False, is_active=True).update(is_active=False)
