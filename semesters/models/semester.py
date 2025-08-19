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
        related_name="semesters",
        verbose_name="مؤسسه"
    )

    title = models.CharField(
        max_length=255,
        help_text="Title of the semester, e.g., \'Fall 1403\'",
        verbose_name="عنوان"
    )

    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")

    is_active = models.BooleanField(
        default=False,
        help_text="Only one semester per institution can be active",
        verbose_name="فعال"
    )

    class Meta:
        verbose_name = "ترم"
        verbose_name_plural = "ترم‌ها"

    def __str__(self):
        return f"{self.title} - {self.institution.name}"
