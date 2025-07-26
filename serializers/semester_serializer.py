from rest_framework import serializers
from semesters.models import Semester


class SemesterSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and retrieving semester details.
    """

    class Meta:
        model = Semester
        fields = ["id", "title", "start_date", "end_date", "is_active", "institution"]
        read_only_fields = ["id", "institution"]


class CreateSemesterSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new semester.
    """

    class Meta:
        model = Semester
        fields = ["title", "start_date", "end_date", "is_active"]

    def validate(self, data):
        if data.get("start_date") and data.get("end_date"):
            if data["end_date"] < data["start_date"]:
                raise serializers.ValidationError("End date cannot be before start date.")
        return data


class UpdateSemesterSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing semester.
    """

    class Meta:
        model = Semester
        fields = ["title", "start_date", "end_date", "is_active"]

    def validate(self, data):
        start = data.get("start_date", self.instance.start_date)
        end = data.get("end_date", self.instance.end_date)
        if end < start:
            raise serializers.ValidationError("End date cannot be before start date.")
        return data
