from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """Serializer responsible for validating basic login credentials.

    The serializer only accepts the ``username`` and ``password`` fields and
    ensures both values are supplied before the authentication service attempts
    to verify the user.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    # Ensure both username and password values are present before proceeding.
    def validate(self, attrs):
        """Check that both authentication fields are provided in the payload."""
        username = attrs.get("username")
        password = attrs.get("password")

        if not username or not password:
            raise serializers.ValidationError("Both username and password are required.")

        return attrs
