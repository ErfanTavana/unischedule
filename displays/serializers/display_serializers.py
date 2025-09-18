from __future__ import annotations

from typing import Any
from uuid import uuid4

from django.utils import timezone
from rest_framework import serializers

from courses.models import Course
from displays.models import DisplayScreen
from displays.utils import (
    compute_filter_day_of_week,
    compute_filter_week_type,
    sort_filters,
)
from locations.models import Classroom
from professors.models import Professor
from schedules.models import ClassSession
from semesters.models import Semester

DAY_CHOICES = {choice for choice, _ in ClassSession.DAY_OF_WEEK_CHOICES}
WEEK_TYPE_CHOICES = {choice for choice, _ in ClassSession.WeekTypeChoices.choices}


class DisplayFilterConfigSerializer(serializers.Serializer):
    def to_representation(self, instance: dict[str, Any]) -> dict[str, Any]:  # type: ignore[override]
        screen_id = self.context.get("screen_id")
        return {
            "id": instance.get("id"),
            "display_screen": screen_id,
            "title": instance.get("title") or "",
            "classroom": instance.get("classroom"),
            "professor": instance.get("professor"),
            "course": instance.get("course"),
            "semester": instance.get("semester"),
            "day_of_week": instance.get("day_of_week"),
            "week_type": instance.get("week_type"),
            "date_override": instance.get("date_override"),
            "position": instance.get("position", 0),
            "duration_seconds": instance.get("duration_seconds", 0),
            "is_active": instance.get("is_active", True),
            "computed_day_of_week": compute_filter_day_of_week(instance),
            "computed_week_type": compute_filter_week_type(instance),
            "created_at": instance.get("created_at"),
            "updated_at": instance.get("updated_at"),
        }


class DisplayFilterConfigWriteSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    title = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    classroom = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), required=False, allow_null=True
    )
    professor = serializers.PrimaryKeyRelatedField(
        queryset=Professor.objects.all(), required=False, allow_null=True
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), required=False, allow_null=True
    )
    semester = serializers.PrimaryKeyRelatedField(
        queryset=Semester.objects.all(), required=False, allow_null=True
    )
    day_of_week = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    week_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    date_override = serializers.DateField(required=False, allow_null=True)
    position = serializers.IntegerField(required=False)
    duration_seconds = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        classroom = attrs.get("classroom")
        professor = attrs.get("professor")
        course = attrs.get("course")
        semester = attrs.get("semester")

        day_of_week = attrs.get("day_of_week")
        if day_of_week == "":
            day_of_week = None
        if day_of_week and day_of_week not in DAY_CHOICES:
            raise serializers.ValidationError({"day_of_week": "روز هفته انتخاب‌شده معتبر نیست."})
        attrs["day_of_week"] = day_of_week

        week_type = attrs.get("week_type")
        if week_type == "":
            week_type = None
        if week_type and week_type not in WEEK_TYPE_CHOICES:
            raise serializers.ValidationError({"week_type": "نوع هفته انتخاب‌شده معتبر نیست."})
        attrs["week_type"] = week_type

        date_override = attrs.get("date_override")

        selectors = [
            classroom,
            professor,
            course,
            semester,
            day_of_week,
            week_type,
            date_override,
        ]
        if not any(selectors):
            raise serializers.ValidationError("حداقل یکی از معیارهای فیلتر باید مشخص شود.")

        institution = self.context.get("institution")
        errors = {}
        if institution:
            if classroom and classroom.building.institution != institution:
                errors["classroom"] = "کلاس انتخاب‌شده متعلق به این مؤسسه نیست."
            if professor and professor.institution != institution:
                errors["professor"] = "استاد انتخاب‌شده متعلق به این مؤسسه نیست."
            if course and course.institution != institution:
                errors["course"] = "درس انتخاب‌شده متعلق به این مؤسسه نیست."
            if semester and semester.institution != institution:
                errors["semester"] = "ترم انتخاب‌شده متعلق به این مؤسسه نیست."

        if errors:
            raise serializers.ValidationError(errors)

        position = attrs.get("position", 0)
        if position is None:
            position = 0
        if position < 0:
            raise serializers.ValidationError({"position": "ترتیب نمایش نمی‌تواند منفی باشد."})
        attrs["position"] = position

        duration = attrs.get("duration_seconds", 0)
        if duration is None:
            duration = 0
        if duration < 0:
            raise serializers.ValidationError({"duration_seconds": "مدت نمایش نمی‌تواند منفی باشد."})
        attrs["duration_seconds"] = duration

        if "is_active" not in attrs:
            attrs["is_active"] = True

        return attrs


class DisplayScreenSerializer(serializers.ModelSerializer):
    filters = serializers.SerializerMethodField()

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
            "filters",
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
        )

    def get_filters(self, obj: DisplayScreen) -> list[dict[str, Any]]:
        filters_data = obj.filters or []
        serializer = DisplayFilterConfigSerializer(
            sort_filters(filters_data),
            many=True,
            context={"screen_id": obj.id},
        )
        return serializer.data


class DisplayScreenWriteSerializer(serializers.ModelSerializer):
    filters = DisplayFilterConfigWriteSerializer(many=True, required=False)

    class Meta:
        model = DisplayScreen
        fields = [
            "title",
            "refresh_interval",
            "layout_theme",
            "is_active",
            "filters",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        filters_field = self.fields.get("filters")
        if filters_field and hasattr(filters_field, "child"):
            filters_field.child.context.update(self.context)

    def validate_refresh_interval(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("بازه تازه‌سازی باید بزرگتر از صفر باشد.")
        return value

    def create(self, validated_data: dict[str, Any]) -> DisplayScreen:
        filters_data = validated_data.pop("filters", [])
        screen = DisplayScreen.objects.create(**validated_data)
        if filters_data:
            screen.filters = self._prepare_filters(filters_data)
            screen.save(update_fields=["filters"])
        return screen

    def update(self, instance: DisplayScreen, validated_data: dict[str, Any]) -> DisplayScreen:
        filters_data = validated_data.pop("filters", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if filters_data is not None:
            instance.filters = self._prepare_filters(filters_data, instance=instance)
        instance.save()
        return instance

    def _prepare_filters(
        self,
        filters_data: list[dict[str, Any]],
        *,
        instance: DisplayScreen | None = None,
    ) -> list[dict[str, Any]]:
        now_iso = timezone.now().isoformat()
        existing: dict[str, dict[str, Any]] = {}
        if instance and isinstance(instance.filters, list):
            for item in instance.filters:
                identifier = str(item.get("id")) if item.get("id") else None
                if identifier:
                    existing[identifier] = item

        prepared: list[dict[str, Any]] = []
        for raw in filters_data:
            filter_id = raw.get("id") or str(uuid4())
            source = existing.get(filter_id)
            classroom = raw.get("classroom")
            if classroom is not None and hasattr(classroom, "pk"):
                classroom = classroom.pk
            professor = raw.get("professor")
            if professor is not None and hasattr(professor, "pk"):
                professor = professor.pk
            course = raw.get("course")
            if course is not None and hasattr(course, "pk"):
                course = course.pk
            semester = raw.get("semester")
            if semester is not None and hasattr(semester, "pk"):
                semester = semester.pk

            date_override = raw.get("date_override")
            if date_override:
                date_override_value = date_override.isoformat()
            else:
                date_override_value = None

            prepared.append(
                {
                    "id": str(filter_id),
                    "title": (raw.get("title") or ""),
                    "classroom": classroom,
                    "professor": professor,
                    "course": course,
                    "semester": semester,
                    "day_of_week": raw.get("day_of_week"),
                    "week_type": raw.get("week_type"),
                    "date_override": date_override_value,
                    "position": raw.get("position", 0),
                    "duration_seconds": raw.get("duration_seconds", 0),
                    "is_active": raw.get("is_active", True),
                    "created_at": source.get("created_at") if source else now_iso,
                    "updated_at": now_iso,
                }
            )

        return sort_filters(prepared)


class DisplayPublicFilterSerializer(serializers.Serializer):
    def to_representation(self, instance: dict[str, Any]) -> dict[str, Any]:  # type: ignore[override]
        return {
            "title": instance.get("title") or "",
            "computed_day_of_week": compute_filter_day_of_week(instance),
            "computed_week_type": compute_filter_week_type(instance),
            "duration_seconds": instance.get("duration_seconds", 0),
            "position": instance.get("position", 0),
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
    filters = DisplayPublicFilterSerializer(many=True, read_only=True)
    sessions = DisplayPublicSessionSerializer(many=True, read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):  # type: ignore[override]
        generated_at_field = self.fields["generated_at"]
        return {
            "screen": DisplayScreenSerializer(instance["screen"]).data,
            "filters": DisplayPublicFilterSerializer(instance["filters"], many=True).data,
            "sessions": DisplayPublicSessionSerializer(instance["sessions"], many=True).data,
            "generated_at": generated_at_field.to_representation(instance["generated_at"]),
        }
