from django.db import models
from unischedule.core.base_model import BaseModel
from institutions.models import Institution


class Semester(BaseModel):
    """
    Represents an academic semester related to an institution.
    Used for grouping weekly class schedules under a specific time period.
    """

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="semesters"
    )

    title = models.CharField(
        max_length=255,
        help_text="Title of the semester, e.g., 'Fall 1403'"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_active = models.BooleanField(
        default=False,
        help_text="Only one semester per institution can be active"
    )

    class Meta:
        verbose_name = "Semester"
        verbose_name_plural = "Semesters"

    def __str__(self):
        return f"{self.title} - {self.institution.name}"
