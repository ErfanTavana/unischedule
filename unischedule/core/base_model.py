from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    """
    Custom manager that returns only non-deleted records by default.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    """
    Abstract base model with common fields and soft delete functionality.
    Includes timestamp fields and cascade soft delete logic.
    """

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    # Managers
    objects = ActiveManager()           # Default manager: active records only
    objects_with_deleted = models.Manager()  # Includes deleted records

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Perform a soft delete by setting is_deleted=True instead of removing from database.
        """
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

        # Optional: cascade soft delete to related objects
        self._cascade_soft_delete()

    def _cascade_soft_delete(self):
        """
        Override this method in child models to apply soft delete to related objects.
        """
        pass
