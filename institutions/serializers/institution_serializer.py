from django.utils.text import slugify
from rest_framework import serializers

from institutions.models import Institution


class InstitutionSerializer(serializers.ModelSerializer):
    """Serialize institution instances for API responses."""

    class Meta:
        model = Institution
        fields = ("id", "name", "slug", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class BaseInstitutionSerializer(serializers.ModelSerializer):
    """Shared validation utilities for create/update serializers."""

    class Meta:
        model = Institution
        fields = ("name", "slug", "is_active")

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
