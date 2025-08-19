from django.db import models
from unischedule.core.base_model import BaseModel
from institutions.models import Institution
from professors.models import Professor


class Course(BaseModel):
    """
    Represents a university course offering by a specific professor under a specific institution.
    """

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="مؤسسه",
    )
    code = models.CharField(max_length=10, verbose_name="کد")
    title = models.CharField(max_length=255, verbose_name="عنوان")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, verbose_name="استاد")
    offer_code = models.CharField(max_length=20, unique=True, verbose_name="کد ارائه")
    unit_count = models.PositiveSmallIntegerField(default=3, verbose_name="تعداد واحد")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "درس"
        verbose_name_plural = "دروس"

    def __str__(self):
        return f"{self.title} ({self.offer_code})"
