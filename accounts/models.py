from django.contrib.auth.models import AbstractUser
from django.db import models
from institutions.models import Institution


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds a relation to Institution for multi-tenant access control.
    """

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        help_text="The institution this user belongs to."
    )

    def __str__(self):
        return f"{self.username} ({self.institution.name if self.institution else 'No Institution'})"
