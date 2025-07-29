from rest_framework import serializers
from courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """
    Serializer for returning course data in API responses.
    """

    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "title",
            "offer_code",
            "unit_count",
            "is_active",
            "professor",
            "institution",
        ]


class CreateCourseSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new course.
    """

    class Meta:
        model = Course
        fields = [
            "code",
            "title",
            "offer_code",
            "unit_count",
            "is_active",
            "professor",
        ]

    def validate_code(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("کد درس باید فقط شامل حروف و اعداد باشد.")
        return value

    def validate_offer_code(self, value):
        if not value:
            raise serializers.ValidationError("کد ارائه نمی‌تواند خالی باشد.")
        return value


class UpdateCourseSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing course.
    """

    class Meta:
        model = Course
        fields = [
            "title",
            "offer_code",
            "unit_count",
            "is_active",
            "professor",
        ]
        extra_kwargs = {
            "title": {"required": False},
            "offer_code": {"required": False},
            "unit_count": {"required": False},
            "is_active": {"required": False},
            "professor": {"required": False},
        }
