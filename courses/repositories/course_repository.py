from courses.models import Course


def create_course(data: dict) -> Course:
    """
    Create a new course using the given validated data.
    """
    return Course.objects.create(**data)


def get_course_by_id_and_institution(course_id: int, institution) -> Course | None:
    """
    Retrieve a course by ID and institution, excluding soft-deleted ones.
    """
    return Course.objects.filter(id=course_id, institution=institution, is_deleted=False).first()


def list_courses_by_institution(institution) -> list[Course]:
    """
    List all courses belonging to the specified institution.
    """
    return Course.objects.filter(institution=institution, is_deleted=False).order_by("-created_at")


def update_course_fields(course: Course, fields: dict) -> Course:
    """
    Manually update fields of a course and save.
    """
    for key, value in fields.items():
        setattr(course, key, value)
    course.save()
    return course


def soft_delete_course(course: Course) -> None:
    """
    Soft delete a course by setting is_deleted=True.
    """
    course.is_deleted = True
    course.save()
