from rest_framework import serializers
from professors.models import Professor


class ProfessorSerializer(serializers.ModelSerializer):
    """
    Serializer for representing professor data in API responses.

    Fields:
        id: Database identifier exposed to clients.
        first_name: Professor's given name.
        last_name: Professor's family name.
        national_code: National identification number used for uniqueness.
        phone_number: Contact phone for the professor.
        institution: Foreign key reference to the owning institution.
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

    Fields:
        first_name, last_name: Personal information required to register the professor.
        national_code: Must be unique per institution and exactly 10 digits.
        phone_number: Optional contact number captured at creation time.
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
        """Ensure the national code has the correct format and is unique per institution."""
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

    Fields:
        first_name, last_name, phone_number: All optional to support partial updates
        while other immutable fields (national_code, institution) remain unchanged.
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
