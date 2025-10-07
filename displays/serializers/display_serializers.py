from __future__ import annotations

from typing import Any

from rest_framework import serializers

from courses.models import Course
from displays.models import DisplayScreen
from displays.utils import compute_filter_day_of_week, compute_filter_week_type
from locations.models import Building, Classroom
from professors.models import Professor
from schedules.models import ClassSession
from semesters.models import Semester

DAY_CHOICES = {choice for choice, _ in ClassSession.DAY_OF_WEEK_CHOICES}
WEEK_TYPE_CHOICES = {choice for choice, _ in ClassSession.WeekTypeChoices.choices}


class DisplayScreenSerializer(serializers.ModelSerializer):
    """Expose screen configuration alongside computed filter metadata.

    ``filter_computed_day_of_week`` و ``filter_computed_week_type`` فیلدهای
    محاسباتی هستند که مقدار نهایی فیلتر را پس از اعمال منطق کمکی
    ``displays.utils`` باز می‌گردانند تا کلاینت از وضعیت واقعی فیلتر مطلع
    شود.
    """

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
            "filter_building",
            "filter_course",
            "filter_professor",
            "filter_semester",
            "filter_day_of_week",
            "filter_week_type",
            "filter_date_override",
            "filter_start_time",
            "filter_end_time",
            "filter_group_code",
            "filter_capacity",
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
    """Allow administrators to configure selector-based filters for a screen.

    این سریالایزر فیلدهای کلیدخارجی (کلاس، ساختمان، درس و ...) را در قالب
    شناسه دریافت می‌کند و همچنین فیلدهای زمانی، بازهٔ ظرفیت و پارامترهای
    کنترلی نظیر ``filter_is_active`` را اعتبارسنجی می‌کند.  ساختار فیلتر به
    صورت مجموعه‌ای از selectorها است که فعال بودنشان از طریق فلگ
    ``filter_is_active`` تعیین می‌شود.
    """

    filter_classroom = serializers.PrimaryKeyRelatedField(
        queryset=Classroom.objects.all(), required=False, allow_null=True
    )
    filter_building = serializers.PrimaryKeyRelatedField(
        queryset=Building.objects.all(), required=False, allow_null=True
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
    filter_start_time = serializers.TimeField(required=False, allow_null=True)
    filter_end_time = serializers.TimeField(required=False, allow_null=True)
    filter_group_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    filter_capacity = serializers.IntegerField(required=False, allow_null=True, min_value=0)
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
            "filter_building",
            "filter_course",
            "filter_professor",
            "filter_semester",
            "filter_day_of_week",
            "filter_week_type",
            "filter_date_override",
            "filter_start_time",
            "filter_end_time",
            "filter_group_code",
            "filter_capacity",
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

        group_code = attrs.get("filter_group_code", serializers.empty)
        if group_code is not serializers.empty:
            if not group_code:
                attrs["filter_group_code"] = None
            else:
                attrs["filter_group_code"] = str(group_code).strip()
                if not attrs["filter_group_code"]:
                    attrs["filter_group_code"] = None

        start_time = attrs.get("filter_start_time", serializers.empty)
        end_time = attrs.get("filter_end_time", serializers.empty)
        if start_time is not serializers.empty and end_time is not serializers.empty:
            if start_time and end_time and start_time > end_time:
                raise serializers.ValidationError(
                    {
                        "filter_end_time": "زمان پایان نمی‌تواند قبل از زمان شروع باشد.",
                    }
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

        selectors = {
            "filter_classroom": _resolve("filter_classroom"),
            "filter_building": _resolve("filter_building"),
            "filter_professor": _resolve("filter_professor"),
            "filter_course": _resolve("filter_course"),
            "filter_semester": _resolve("filter_semester"),
            "filter_day_of_week": _resolve("filter_day_of_week"),
            "filter_week_type": _resolve("filter_week_type"),
            "filter_date_override": _resolve("filter_date_override"),
            "filter_group_code": _resolve("filter_group_code"),
            "filter_start_time": _resolve("filter_start_time"),
            "filter_end_time": _resolve("filter_end_time"),
            "filter_capacity": _resolve("filter_capacity"),
        }

        def _has_value(value: Any) -> bool:
            if value is None:
                return False
            if isinstance(value, str):
                return value.strip() != ""
            return True

        has_selector = any(_has_value(value) for value in selectors.values())

        if not has_selector:
            if filter_is_active:
                attrs["filter_is_active"] = False
                filter_is_active = False
            else:
                attrs.setdefault("filter_is_active", False)

        if bool(filter_is_active) and not has_selector:
            raise serializers.ValidationError("حداقل یکی از معیارهای فیلتر باید مشخص شود.")

        institution = self._institution()
        errors: dict[str, str] = {}
        if institution:
            classroom = attrs.get("filter_classroom")
            if classroom and classroom.building.institution_id != institution.id:
                errors["filter_classroom"] = "کلاس انتخاب‌شده متعلق به این مؤسسه نیست."

            building_provided = "filter_building" in attrs
            building = attrs.get("filter_building") if building_provided else None
            if not building_provided and instance is not None:
                building = instance.filter_building

            if building and building.institution_id != institution.id:
                errors["filter_building"] = "ساختمان انتخاب‌شده متعلق به این مؤسسه نیست."

            classroom_provided = "filter_classroom" in attrs
            resolved_classroom = classroom if classroom_provided else None
            if not classroom_provided and instance is not None:
                resolved_classroom = instance.filter_classroom

            if resolved_classroom and building and resolved_classroom.building_id != building.id:
                errors["filter_classroom"] = "کلاس و ساختمان انتخاب‌شده هم‌خوانی ندارند."

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
    """Provide the public representation of the configured filters.

    خروجی شامل شناسه و برچسب برای selectorهای فعال است و علاوه بر مقادیر
    خام، فیلدهای محاسباتی ``computed_day_of_week`` و ``computed_week_type`` را
    نیز ارائه می‌دهد تا نحوهٔ اعمال فیلتر برای بیننده شفاف باشد.
    """

    def to_representation(self, instance: DisplayScreen) -> dict[str, Any]:  # type: ignore[override]
        def _ref(attr: str, *, display: str | None = None) -> dict[str, Any] | None:
            value = getattr(instance, attr)
            if not value:
                return None
            label: str
            if display is not None:
                label = display
            elif hasattr(value, "title"):
                label = getattr(value, "title")
            else:
                label = str(value)
            return {"id": value.id, "label": label}

        professor = instance.filter_professor
        professor_label = None
        if professor:
            computed_name = f"{professor.first_name} {professor.last_name}".strip()
            professor_label = computed_name or None

        return {
            "title": instance.filter_title or "",
            "classroom": _ref("filter_classroom"),
            "building": _ref("filter_building"),
            "course": _ref("filter_course"),
            "professor": _ref("filter_professor", display=professor_label),
            "semester": _ref("filter_semester"),
            "group_code": instance.filter_group_code or None,
            "start_time": instance.filter_start_time.isoformat()
            if instance.filter_start_time
            else None,
            "end_time": instance.filter_end_time.isoformat()
            if instance.filter_end_time
            else None,
            "capacity": instance.filter_capacity,
            "computed_day_of_week": compute_filter_day_of_week(instance),
            "computed_week_type": compute_filter_week_type(instance),
            "day_of_week": instance.filter_day_of_week,
            "week_type": instance.filter_week_type,
            "date_override": instance.filter_date_override.isoformat()
            if instance.filter_date_override
            else None,
            "duration_seconds": instance.filter_duration_seconds,
            "is_active": instance.filter_is_active,
        }


class DisplayPublicSessionSerializer(serializers.ModelSerializer):
    """Serialize session data enriched with display-friendly labels."""

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
    """Wrap the screen, filter summary and session list for public displays.

    ساختار نهایی شامل اطلاعات صفحه، توضیح فیلتر به کمک
    ``DisplayPublicFilterSerializer`` و آرایه‌ای از جلسات است که هر کدام با
    فیلدهای محاسباتی از جمله عناوین درس و ساختمان ارائه می‌شوند.
    """

    screen = DisplayScreenSerializer(read_only=True)
    filter = serializers.SerializerMethodField()
    sessions = DisplayPublicSessionSerializer(many=True, read_only=True)
    generated_at = serializers.DateTimeField(read_only=True)

    def get_filter(self, instance: dict[str, Any]) -> dict[str, Any] | None:
        screen = instance.get("filter") or instance.get("screen")
        if not screen:
            return None
        return DisplayPublicFilterSerializer(screen).data
