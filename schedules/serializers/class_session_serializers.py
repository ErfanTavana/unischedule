from rest_framework import serializers
from schedules.models import ClassSession


class ClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = [
            "id",
            "institution",
            "course",
            "professor",
            "classroom",
            "semester",
            "day_of_week",
            "start_time",
            "end_time",
            "week_type",
            "group_code",
            "capacity",
            "note",
        ]


class CreateClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = [
            "course",
            "professor",
            "classroom",
            "semester",
            "day_of_week",
            "start_time",
            "end_time",
            "week_type",
            "group_code",
            "capacity",
            "note",
        ]

    def validate(self, attrs):
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and start >= end:
            raise serializers.ValidationError("زمان شروع باید قبل از زمان پایان باشد.")
        return attrs


class UpdateClassSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSession
        fields = [
            "course",
            "professor",
            "classroom",
            "semester",
            "day_of_week",
            "start_time",
            "end_time",
            "week_type",
            "group_code",
            "capacity",
            "note",
        ]
        extra_kwargs = {f: {"required": False} for f in fields}

    def validate(self, attrs):
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and start >= end:
            raise serializers.ValidationError("زمان شروع باید قبل از زمان پایان باشد.")
        return attrs
