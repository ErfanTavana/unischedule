from __future__ import annotations

from typing import Any

from rest_framework import serializers

from courses.models import Course
from displays.models import DisplayScreen
from displays.utils import compute_filter_day_of_week, compute_filter_week_type
from locations.models import Classroom
from professors.models import Professor
from schedules.models import ClassSession
from semesters.models import Semester

DAY_CHOICES = {choice for choice, _ in ClassSession.DAY_OF_WEEK_CHOICES}
WEEK_TYPE_CHOICES = {choice for choice, _ in ClassSession.WeekTypeChoices.choices}


class DisplayScreenSerializer(serializers.ModelSerializer):
    filter_computed_day_of_week = serializers.SerializerMethodField()
    filter_computed_week_type = serializers.SerializerMethodField()

    class Meta:
        model = DisplayScreen
        fields = [
            "id",
            "institution",
            "title",
            "slug",
            "access_token",
            "refresh_interval",
            "layout_theme",
            "is_active",
            "filter_title",
            "filter_classroom",
            "filter_course",
            "filter_professor",
            "filter_semester",
            "filter_day_of_week",
            "filter_week_type",
            "filter_date_override",
            "filter_duration_seconds",
            "filter_is_active",
            "filter_computed_day_of_week",
            "filter_computed_week_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "slug",
            "access_token",
            "created_at",
            "updated_at",
            "institution",
            "filter_computed_day_of_week",
            "filter_computed_week_type",
        )

    def get_filter_computed_day_of_week(self, obj: DisplayScreen) -> str | None:
        return compute_filter_day_of_week(obj)

    def get_filter_computed_week_type(self, obj: DisplayScreen) -> str | None:
        return compute_filter_week_type(obj)


class DisplayScreenWriteSerializer(serializers.ModelSerializer):
    filter_classroom = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), required=False, allow_null=True
    )
    filter_course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), required=False, allow_null=True
    )
    filter_professor = serializers.PrimaryKeyRelatedField(
        queryset=Professor.objects.all(), required=False, allow_null=True
    )
    filter_semester = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), required=False, allow_null=True
    )
    filter_day_of_week = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    filter_week_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    filter_date_override = serializers.DateField(required=False, allow_null=True)
    filter_duration_seconds = serializers.IntegerField(required=False, min_value=0)
    filter_is_active = serializers.BooleanField(required=False)

    class Meta:
        model = DisplayScreen
        fields = [
            "title",
            "refresh_interval",
            "layout_theme",
            "is_active",
            "filter_title",
            "filter_classroom",
            "filter_course",
            "filter_professor",
            "filter_semester",
            "filter_day_of_week",
            "filter_week_type",
            "filter_date_override",
            "filter_duration_seconds",
            "filter_is_active",
        ]

    def _institution(self) -> Any:
        if self.instance is not None:
            return self.instance.institution
        return self.context.get("institution")

    def validate_refresh_interval(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("بازه تازه‌سازی باید بزرگتر از صفر باشد.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        instance = self.instance

        day_of_week = attrs.get("filter_day_of_week", serializers.empty)
        if day_of_week is not serializers.empty:
            if not day_of_week:
                attrs["filter_day_of_week"] = None
            elif day_of_week not in DAY_CHOICES:
                raise serializers.ValidationError(
                    {"filter_day_of_week": "روز هفته انتخاب‌شده معتبر نیست."}
                )

        week_type = attrs.get("filter_week_type", serializers.empty)
        if week_type is not serializers.empty:
            if not week_type:
                attrs["filter_week_type"] = None
            elif week_type not in WEEK_TYPE_CHOICES:
                raise serializers.ValidationError(
                    {"filter_week_type": "نوع هفته انتخاب‌شده معتبر نیست."}
                )

        duration = attrs.get("filter_duration_seconds", serializers.empty)
        if duration is serializers.empty and instance is None:
            attrs.setdefault("filter_duration_seconds", 0)

        if "filter_is_active" in attrs:
            provided_is_active = attrs.get("filter_is_active")
            attrs["filter_is_active"] = bool(provided_is_active)
            filter_is_active = bool(provided_is_active)
        else:
            if instance is not None:
                filter_is_active = instance.filter_is_active
            else:
                filter_is_active = True

        def _resolve(field: str) -> Any:
            if field in attrs:
                return attrs[field]
            if instance is not None:
                return getattr(instance, field)
            return None

        selectors = [
            _resolve("filter_classroom"),
            _resolve("filter_professor"),
            _resolve("filter_course"),
            _resolve("filter_semester"),
            _resolve("filter_day_of_week"),
            _resolve("filter_week_type"),
            _resolve("filter_date_override"),
        ]

        if bool(filter_is_active) and not any(selectors):
            raise serializers.ValidationError("حداقل یکی از معیارهای فیلتر باید مشخص شود.")

        institution = self._institution()
        errors: dict[str, str] = {}
        if institution:
            classroom = attrs.get("filter_classroom")
            if classroom and classroom.building.institution_id != institution.id:
                errors["filter_classroom"] = "کلاس انتخاب‌شده متعلق به این مؤسسه نیست."

            professor = attrs.get("filter_professor")
            if professor and professor.institution_id != institution.id:
                errors["filter_professor"] = "استاد انتخاب‌شده متعلق به این مؤسسه نیست."

            course = attrs.get("filter_course")
            if course and course.institution_id != institution.id:
                errors["filter_course"] = "درس انتخاب‌شده متعلق به این مؤسسه نیست."

            semester = attrs.get("filter_semester")
            if semester and semester.institution_id != institution.id:
                errors["filter_semester"] = "ترم انتخاب‌شده متعلق به این مؤسسه نیست."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs


class DisplayPublicFilterSerializer(serializers.Serializer):
    def to_representation(self, instance: DisplayScreen) -> dict[str, Any]:  # type: ignore[override]
        return {
            "title": instance.filter_title or "",
            "computed_day_of_week": compute_filter_day_of_week(instance),
            "computed_week_type": compute_filter_week_type(instance),
            "duration_seconds": instance.filter_duration_seconds,
            "is_active": instance.filter_is_active,
        }


class DisplayPublicSessionSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    professor_name = serializers.SerializerMethodField()
    classroom_title = serializers.CharField(source="classroom.title", read_only=True)
    building_title = serializers.CharField(source="classroom.building.title", read_only=True)

    class Meta:
        model = ClassSession
        fields = [
            "id",
            "course_title",
            "professor_name",
            "day_of_week",
            "start_time",
            "end_time",
            "week_type",
            "classroom_title",
            "building_title",
            "group_code",
            "note",
        ]
        read_only_fields = fields

    def get_professor_name(self, obj: ClassSession) -> str:
        return f"{obj.professor.first_name} {obj.professor.last_name}".strip()


class DisplayPublicPayloadSerializer(serializers.Serializer):
    screen = DisplayScreenSerializer(read_only=True)
    filter = serializers.SerializerMethodField()
    sessions = DisplayPublicSessionSerializer(many=True, read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)

    def get_filter(self, instance: dict[str, Any]) -> dict[str, Any] | None:
        screen = instance.get("filter") or instance.get("screen")
        if not screen:
            return None
        return DisplayPublicFilterSerializer(screen).data
