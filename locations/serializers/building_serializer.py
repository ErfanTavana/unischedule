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

    def validate_title(self, value):
        institution = self.context.get("institution")
        if institution and Building.objects.filter(
            institution=institution, title=value
        ).exists():
            raise serializers.ValidationError(
                "عنوان ساختمان در این مؤسسه تکراری است."
            )
        return value

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

    def validate_title(self, value):
        if value is None:
            return value
        institution = getattr(self.instance, "institution", None)
        if (
            institution
            and Building.objects.filter(
                institution=institution, title=value
            )
            .exclude(id=self.instance.id)
            .exists()
        ):
            raise serializers.ValidationError(
                "عنوان ساختمان در این مؤسسه تکراری است."
            )
        return value
