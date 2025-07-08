from django.db import models
from unischedule.core.base_model import BaseModel


class Institution(BaseModel):
    """
    Represents an educational institution (e.g., university, college, academy).
    Each semester and related data are associated with a specific institution.
    """

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"

    def __str__(self):
        return self.name
