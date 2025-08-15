from rest_framework import serializers
from locations.models import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    """
    Serializer for representing classroom data in API responses.
    """

    class Meta:
        model = Classroom
        fields = [
            "id",
            "title",
            "building",
        ]


class CreateClassroomSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new classroom.
    """

    class Meta:
        model = Classroom
        fields = [
            "title",
        ]


class UpdateClassroomSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing classroom.
    """

    class Meta:
        model = Classroom
        fields = [
            "title",
        ]
        extra_kwargs = {
            "title": {"required": False},
        }
