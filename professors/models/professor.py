from django.db import models
from unischedule.core.base_model import BaseModel
from institutions.models import Institution


class Professor(BaseModel):
    """
    Represents a university professor. Each professor belongs to an institution.
    """

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="professors",
        verbose_name="مؤسسه",
    )
    first_name = models.CharField(max_length=100, verbose_name="نام")
    last_name = models.CharField(max_length=100, verbose_name="نام خانوادگی")
    national_code = models.CharField(max_length=10, unique=True, verbose_name="کد ملی")
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name="شماره تلفن",
    )

    class Meta:
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
