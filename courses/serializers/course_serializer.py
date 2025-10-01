from rest_framework import serializers
from courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """Read-only serializer exposing the persisted attributes of a course.

    No computed or derived fields are defined; each attribute maps directly to
    a column on :class:`courses.models.Course` so the consumer receives the
    exact database values.
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
    """Input serializer for course creation requests.

    All fields correspond to model attributes and are validated in place. The
    serializer does not inject computed data; instead, the service layer assigns
    the owning institution before persisting the model.
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
    """Serializer for partial updates on existing course records.

    Every exposed field maps directly to the model; no computed values are
    produced. ``extra_kwargs`` relaxes required flags so callers can send only
    the fields they intend to modify.
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
