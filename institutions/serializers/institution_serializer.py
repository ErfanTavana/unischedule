from django.utils.text import slugify
from rest_framework import serializers

from institutions.models import Institution


class InstitutionSerializer(serializers.ModelSerializer):
    """Serialize institution instances for API responses."""

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = (
            "id",
            "name",
            "slug",
            "logo",
            "logo_url",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "logo_url")

    def get_logo_url(self, obj: Institution) -> str | None:
        if not obj.logo:
            return None
        request = self.context.get("request") if hasattr(self, "context") else None
        try:
            url = obj.logo.url
        except ValueError:
            return None
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class BaseInstitutionSerializer(serializers.ModelSerializer):
    """Shared validation utilities for create/update serializers."""

    class Meta:
        model = Institution
        fields = ("name", "slug", "is_active", "logo")
        extra_kwargs = {
            "logo": {"required": False, "allow_null": True},
        }

    def validate_slug(self, value: str) -> str:
        """Normalize the slug and ensure it stays unique among active institutions."""

        normalized = slugify(value)
        instance = getattr(self, "instance", None)
        queryset = Institution.objects.filter(slug=normalized)
        if instance is not None:
            queryset = queryset.exclude(pk=instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("Slug already exists for another institution.")
        return normalized

    def validate_name(self, value: str) -> str:
        """Trim whitespace to avoid accidental duplicates based on trailing spaces."""

        return value.strip()


class CreateInstitutionSerializer(BaseInstitutionSerializer):
    """Serializer used for institution creation flows."""

    is_active = serializers.BooleanField(default=True)


class UpdateInstitutionSerializer(BaseInstitutionSerializer):
    """Serializer used when updating an existing institution instance."""

    def update(self, instance: Institution, validated_data: dict) -> Institution:
        """Apply validated changes to the provided instance."""

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class InstitutionLogoSerializer(serializers.ModelSerializer):
    """Dedicated serializer for exposing and mutating institution logos."""

    logo = serializers.FileField(required=False, allow_null=True, write_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = ("id", "name", "slug", "logo", "logo_url")
        read_only_fields = ("id", "name", "slug", "logo_url")

    def get_logo_url(self, obj: Institution) -> str | None:
        if not obj.logo:
            return None
        request = self.context.get("request") if hasattr(self, "context") else None
        try:
            url = obj.logo.url
        except ValueError:
            return None
        if request is not None:
            return request.build_absolute_uri(url)
        return url
