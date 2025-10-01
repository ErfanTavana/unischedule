from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer that validates password change payloads for authenticated users.

    The serializer expects the caller to provide the current password alongside
    the desired new password (and its confirmation). It also leverages Django's
    built-in password validators to enforce complexity policies.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    # Perform cross-field validation to ensure the new password is acceptable.
    def validate(self, attrs):
        """Validate that the new password is confirmed and meets policy requirements."""
        old_password = attrs.get("old_password")
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")
        user = self.context.get("user")

        errors = {}

        if new_password != confirm_new_password:
            errors["confirm_new_password"] = ["رمز عبور جدید و تکرار آن یکسان نیستند."]

        if old_password and new_password and old_password == new_password:
            errors.setdefault("new_password", []).append(
                "رمز عبور جدید نباید با رمز عبور فعلی یکسان باشد."
            )

        try:
            password_validation.validate_password(new_password, user=user)
        except DjangoValidationError as exc:
            errors.setdefault("new_password", []).extend(exc.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return attrs
