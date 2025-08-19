from rest_framework import serializers
from professors.models import Professor


class ProfessorSerializer(serializers.ModelSerializer):
    """
    Serializer for representing professor data in API responses.
    """
    class Meta:
        model = Professor
        fields = [
            "id",
            "first_name",
            "last_name",
            "national_code",
            "phone_number",
            "institution",
        ]


class CreateProfessorSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new professor.
    """

    class Meta:
        model = Professor
        fields = [
            "first_name",
            "last_name",
            "national_code",
            "phone_number",
        ]

    def validate_national_code(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("کد ملی باید ۱۰ رقم و فقط عدد باشد.")

        institution = self.context.get("institution")
        if (
            institution
            and Professor.objects.filter(national_code=value, institution=institution).exists()
        ):
            raise serializers.ValidationError(
                "استادی با این کد ملی در این مؤسسه وجود دارد."
            )
        return value


class UpdateProfessorSerializer(serializers.ModelSerializer):
    """
    Serializer for updating professor details.
    """

    class Meta:
        model = Professor
        fields = [
            "first_name",
            "last_name",
            "phone_number",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
            "phone_number": {"required": False},
        }
