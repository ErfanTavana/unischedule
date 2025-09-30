from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
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
