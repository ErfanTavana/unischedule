from django.db import models
from unischedule.core.base_model import BaseModel
from institutions.models import Institution


class Building(BaseModel):
    """
    Represents a physical building for holding classes (e.g., دانشکده علوم، ساختمان شماره ۲).
    Each building belongs to a specific institution.
    """

    title = models.CharField(max_length=255, help_text="ساختمان آموزشی شماره یک",
                             unique=False)  # e.g., "ساختمان آموزشی شماره ۲"
    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="buildings"
    )

    class Meta:
        verbose_name = "ساختمان"
        verbose_name_plural = "ساختمان‌ها"

    def __str__(self):
        return self.title
