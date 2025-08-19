from django.db import models
from unischedule.core.base_model import BaseModel


class Institution(BaseModel):
    """
    Represents an educational institution (e.g., university, college, academy).
    Each semester and related data are associated with a specific institution.
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="نام")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="نامک")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "مؤسسه"
        verbose_name_plural = "مؤسسات"

    def __str__(self):
        return self.name
