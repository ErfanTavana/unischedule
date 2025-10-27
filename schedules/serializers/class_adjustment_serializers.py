from __future__ import annotations

from datetime import date

from rest_framework import serializers

from locations.models import Classroom
from schedules.models import ClassSession, ClassCancellation, MakeupClassSession


class ClassCancellationSerializer(serializers.ModelSerializer):
    """نمایش جزئیات لغو جلسه."""

    class_session_title = serializers.CharField(
        source="class_session.course.title", read_only=True
    )
    professor_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassCancellation
        fields = [
            "id",
            "institution",
            "class_session",
            "class_session_title",
            "professor_name",
            "date",
            "reason",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_professor_name(self, obj: ClassCancellation) -> str:
        professor = obj.class_session.professor
        return f"{professor.first_name} {professor.last_name}".strip()


class BaseClassCancellationWriteSerializer(serializers.ModelSerializer):
    class_session = serializers.PrimaryKeyRelatedField(queryset=ClassSession.objects.all())

    class Meta:
        model = ClassCancellation
        fields = ["class_session", "date", "reason", "note"]

    def _resolve_session(self) -> ClassSession | None:
        candidate = self.initial_data.get("class_session")
        if candidate in (None, ""):
            return getattr(self.instance, "class_session", None)
        if isinstance(candidate, ClassSession):
            return candidate
        try:
            return ClassSession.objects.filter(pk=candidate).select_related("semester").first()
        except Exception:  # pragma: no cover - defensive
            return getattr(self.instance, "class_session", None)

    def validate_date(self, value: date) -> date:
        session_instance = self._resolve_session()
        if session_instance and session_instance.semester and session_instance.semester.start_date and session_instance.semester.end_date:
            if not (session_instance.semester.start_date <= value <= session_instance.semester.end_date):
                raise serializers.ValidationError("تاریخ لغو باید در محدوده ترم مربوطه باشد.")
        return value


class CreateClassCancellationSerializer(BaseClassCancellationWriteSerializer):
    pass


class UpdateClassCancellationSerializer(BaseClassCancellationWriteSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class MakeupClassSessionSerializer(serializers.ModelSerializer):
    """جزئیات جلسه جبرانی."""

    class_session_title = serializers.CharField(
        source="class_session.course.title", read_only=True
    )
    professor_name = serializers.SerializerMethodField()
    building_title = serializers.CharField(
        source="classroom.building.title", read_only=True
    )

    class Meta:
        model = MakeupClassSession
        fields = [
            "id",
            "institution",
            "class_session",
            "class_session_title",
            "professor_name",
            "date",
            "start_time",
            "end_time",
            "classroom",
            "building_title",
            "group_code",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_professor_name(self, obj: MakeupClassSession) -> str:
        professor = obj.class_session.professor
        return f"{professor.first_name} {professor.last_name}".strip()


class BaseMakeupClassSessionWriteSerializer(serializers.ModelSerializer):
    class_session = serializers.PrimaryKeyRelatedField(queryset=ClassSession.objects.all())
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())

    class Meta:
        model = MakeupClassSession
        fields = [
            "class_session",
            "date",
            "start_time",
            "end_time",
            "classroom",
            "group_code",
            "note",
        ]

    def validate(self, attrs: dict) -> dict:
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and start >= end:
            raise serializers.ValidationError("زمان شروع باید قبل از زمان پایان باشد.")
        return attrs

    def validate_classroom(self, value: Classroom) -> Classroom:
        institution = self.context.get("institution")
        if institution and value.building.institution_id != institution.id:
            raise serializers.ValidationError("کلاس انتخاب‌شده متعلق به این مؤسسه نیست.")
        return value

    def validate_class_session(self, value: ClassSession) -> ClassSession:
        institution = self.context.get("institution")
        if institution and value.institution_id != institution.id:
            raise serializers.ValidationError("جلسه انتخاب‌شده متعلق به این مؤسسه نیست.")
        return value

    def validate_date(self, value: date) -> date:
        session = self.initial_data.get("class_session")
        session_instance: ClassSession | None
        if session in (None, ""):
            session_instance = getattr(self.instance, "class_session", None)
        elif isinstance(session, ClassSession):
            session_instance = session
        else:
            try:
                session_instance = ClassSession.objects.filter(pk=session).select_related("semester").first()
            except Exception:  # pragma: no cover - defensive
                session_instance = getattr(self.instance, "class_session", None)
        if session_instance and session_instance.semester:
            semester = session_instance.semester
            if semester.start_date and semester.end_date:
                if not (semester.start_date <= value <= semester.end_date):
                    raise serializers.ValidationError("تاریخ جلسه باید در محدوده ترم باشد.")
        return value


class CreateMakeupClassSessionSerializer(BaseMakeupClassSessionWriteSerializer):
    pass


class UpdateMakeupClassSessionSerializer(BaseMakeupClassSessionWriteSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False
