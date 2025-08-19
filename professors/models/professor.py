from django.db import models
from unischedule.core.base_model import BaseModel
from institutions.models import Institution


class Professor(BaseModel):
    """
    Represents a university professor. Each professor belongs to an institution.
    """

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="professors")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    national_code = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        verbose_name = "استاد"
        verbose_name_plural = "اساتید"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
