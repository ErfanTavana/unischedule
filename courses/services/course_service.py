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
    """
    Create a new course for a specific institution.
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
    """
    Update an existing course instance.
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
    """
    Return course instance if found, else raise 404 validation error.
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
    """
    Return serialized course if found.
    """
    course = get_course_instance_or_404(course_id, institution)
    return CourseSerializer(course).data


def delete_course(course: Course) -> None:
    """
    Soft delete a course by marking it as deleted.
    """
    course_repository.soft_delete_course(course)


def list_courses(institution) -> list[dict]:
    """
    Return serialized list of all courses for the given institution.
    """
    queryset = course_repository.list_courses_by_institution(institution)
    return CourseSerializer(queryset, many=True).data
