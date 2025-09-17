from __future__ import annotations

from typing import Any

from django.utils import timezone
from rest_framework import serializers

from displays.models import DisplayScreen, DisplayFilter, DisplayMessage
from schedules.models import ClassSession


class DisplayMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayMessage
        fields = [
            "id",
            "content",
            "is_active",
            "priority",
            "starts_at",
            "ends_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at")


class DisplayFilterSerializer(serializers.ModelSerializer):
    computed_day_of_week = serializers.CharField(read_only=True)
    computed_week_type = serializers.CharField(read_only=True)

    class Meta:
        model = DisplayFilter
        fields = [
            "id",
            "display_screen",
            "title",
            "classroom",
            "professor",
            "course",
            "semester",
            "day_of_week",
            "week_type",
            "date_override",
            "position",
            "duration_seconds",
            "is_active",
            "computed_day_of_week",
            "computed_week_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "created_at", "updated_at", "display_screen")


class DisplayFilterWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayFilter
        fields = [
            "title",
            "classroom",
            "professor",
            "course",
            "semester",
            "day_of_week",
            "week_type",
            "date_override",
            "position",
            "duration_seconds",
            "is_active",
        ]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        instance = self.instance

        classroom = attrs.get("classroom", getattr(instance, "classroom", None))
        professor = attrs.get("professor", getattr(instance, "professor", None))
        course = attrs.get("course", getattr(instance, "course", None))
        semester = attrs.get("semester", getattr(instance, "semester", None))
        day_of_week = attrs.get("day_of_week", getattr(instance, "day_of_week", None))
        week_type = attrs.get("week_type", getattr(instance, "week_type", None))
        date_override = attrs.get("date_override", getattr(instance, "date_override", None))

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

        screen: DisplayScreen | None = self.context.get("display_screen") or getattr(instance, "display_screen", None)
        institution = self.context.get("institution") or (screen.institution if screen else None)
        errors = {}

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

        return attrs


class DisplayScreenSerializer(serializers.ModelSerializer):
    filters = DisplayFilterSerializer(many=True, read_only=True)
    messages = DisplayMessageSerializer(many=True, read_only=True)

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
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "slug", "access_token", "created_at", "updated_at", "institution")


class DisplayScreenWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayScreen
        fields = [
            "title",
            "refresh_interval",
            "layout_theme",
            "is_active",
        ]

    def validate_refresh_interval(self, value: int) -> int:
        if value <= 0:
            raise serializers.ValidationError("بازه تازه‌سازی باید بزرگتر از صفر باشد.")
        return value


class DisplayPublicMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayMessage
        fields = ["content", "priority"]


class DisplayPublicFilterSerializer(serializers.ModelSerializer):
    computed_day_of_week = serializers.CharField(read_only=True)
    computed_week_type = serializers.CharField(read_only=True)

    class Meta:
        model = DisplayFilter
        fields = [
            "title",
            "computed_day_of_week",
            "computed_week_type",
            "duration_seconds",
            "position",
        ]
        read_only_fields = fields


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
    messages = DisplayPublicMessageSerializer(many=True, read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):  # type: ignore[override]
        generated_at_field = self.fields["generated_at"]
        return {
            "screen": DisplayScreenSerializer(instance["screen"]).data,
            "filters": DisplayPublicFilterSerializer(instance["filters"], many=True).data,
            "sessions": DisplayPublicSessionSerializer(instance["sessions"], many=True).data,
            "messages": DisplayPublicMessageSerializer(instance["messages"], many=True).data,
            "generated_at": generated_at_field.to_representation(instance["generated_at"]),
        }
