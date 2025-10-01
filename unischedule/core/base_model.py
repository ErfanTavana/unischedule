"""Core abstract models and managers shared across the project.

This module introduces :class:`ActiveManager` and :class:`BaseModel` which are
used by most database models in the project. They encapsulate conventions such
as soft deletion and audit timestamps so that every domain model can inherit a
consistent behaviour without re-implementing it.
"""

from django.db import models
from django.utils import timezone


class ActiveManager(models.Manager):
    """Return only non-deleted rows when accessing ``Model.objects``.

    ``ActiveManager`` keeps application queries focused on active records by
    filtering ``is_deleted=False`` at the ORM level. Developers can access the
    full dataset through ``objects_with_deleted`` when they explicitly need
    archived rows.
    """
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class BaseModel(models.Model):
    """
    Abstract base model that centralises audit fields and soft delete logic.

    Every persistent model inherits the ``created_at``/``updated_at`` timestamp
    pair, a ``is_deleted`` flag that drives soft deletion, and two managers
    (``objects`` and ``objects_with_deleted``). The :meth:`delete` override makes
    sure deletions mark records as archived while the optional
    :meth:`_cascade_soft_delete` hook allows propagating the behaviour to
    related objects (e.g. child schedules) when required.
    """

    created_at = models.DateTimeField(default=timezone.now, verbose_name="ایجاد شده در")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="به‌روزرسانی شده در")
    is_deleted = models.BooleanField(default=False, verbose_name="حذف شده")

    # Managers
    objects = ActiveManager()           # Default manager: active records only
    objects_with_deleted = models.Manager()  # Includes deleted records

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete the record instead of removing it from the database."""
        self.is_deleted = True
        self.save(update_fields=["is_deleted", "updated_at"])

        # Optional: cascade soft delete to related objects
        self._cascade_soft_delete()

    def _cascade_soft_delete(self):
        """Hook for subclasses to soft delete related records when necessary."""
        pass
