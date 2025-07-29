from rest_framework import serializers
from locations.models import Building


class BuildingSerializer(serializers.ModelSerializer):
    """
    Serializer for representing building data in API responses.
    """

    class Meta:
        model = Building
        fields = [
            "id",
            "title",
            "institution",
        ]


class CreateBuildingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new building.
    Includes validation for unique title within the same institution.
    """

    class Meta:
        model = Building
        fields = ["title"]

class UpdateBuildingSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing building.
    """

    class Meta:
        model = Building
        fields = [
            "title",
        ]
        extra_kwargs = {
            "title": {"required": False},
        }
