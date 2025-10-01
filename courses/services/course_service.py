from unischedule.core.exceptions import CustomValidationError
from unischedule.core.error_codes import ErrorCodes
from courses.serializers import (
    CreateCourseSerializer,
    UpdateCourseSerializer,
    CourseSerializer,
)
from courses import repositories as course_repository
from courses.models import Course


def create_course(data: dict, institution) -> dict:
    """Create a course for the given institution after validation.

    The payload is validated with :class:`CreateCourseSerializer`. Any
    validation failure raises :class:`CustomValidationError` populated with the
    ``VALIDATION_FAILED`` error code so the view can return a structured HTTP
    400 response.
    """
    serializer = CreateCourseSerializer(data=data)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    validated_data = serializer.validated_data
    validated_data["institution"] = institution

    course = course_repository.create_course(validated_data)
    return CourseSerializer(course).data


def update_course(course: Course, data: dict) -> dict:
    """Apply partial updates to a course and return the serialized payload.

    The input is validated by :class:`UpdateCourseSerializer`; on error a
    :class:`CustomValidationError` with the ``VALIDATION_FAILED`` metadata is
    raised so the caller can surface field-level issues.
    """
    serializer = UpdateCourseSerializer(instance=course, data=data, partial=True)
    if not serializer.is_valid():
        raise CustomValidationError(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=serializer.errors,
        )

    updated_instance = serializer.save()
    return CourseSerializer(updated_instance).data


def get_course_instance_or_404(course_id: int, institution) -> Course:
    """Return a course instance or raise a not-found error.

    If the course does not exist for the provided institution a
    :class:`CustomValidationError` configured with ``COURSE_NOT_FOUND`` is
    raised, mimicking the semantics of ``Http404`` in API responses.
    """
    course = course_repository.get_course_by_id_and_institution(course_id, institution)
    if not course:
        raise CustomValidationError(
            message=ErrorCodes.COURSE_NOT_FOUND["message"],
            code=ErrorCodes.COURSE_NOT_FOUND["code"],
            status_code=ErrorCodes.COURSE_NOT_FOUND["status_code"],
            errors=ErrorCodes.COURSE_NOT_FOUND["errors"]
        )
    return course


def get_course_by_id_or_404(course_id: int, institution) -> dict:
    """Return serialized course data or propagate the not-found error.

    Delegates to :func:`get_course_instance_or_404` and therefore raises the
    same :class:`CustomValidationError` when the course is missing.
    """
    course = get_course_instance_or_404(course_id, institution)
    return CourseSerializer(course).data


def delete_course(course: Course) -> None:
    """Soft-delete the supplied course by delegating to the repository.

    This function currently relies on the repository layer for error handling
    and therefore will bubble up any unexpected exceptions to the caller.
    """
    course_repository.soft_delete_course(course)


def list_courses(institution) -> list[dict]:
    """Return serialized courses for the institution.

    The repository lookup is expected to succeed; any lower-level exceptions
    (e.g., database errors) are propagated for the caller to handle.
    """
    queryset = course_repository.list_courses_by_institution(institution)
    return CourseSerializer(queryset, many=True).data
