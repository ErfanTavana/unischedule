from django.db import models
from unischedule.core.base_model import BaseModel
from locations.models import Building

class Classroom(BaseModel):
    """
    Represents a physical classroom within a building (e.g., کلاس ۱۰۱، آزمایشگاه کامپیوتر).
    """

    title = models.CharField(
        max_length=100,
        help_text="مثلاً کلاس ۱۰۱ یا آزمایشگاه شبکه",
        verbose_name="عنوان",
    )
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="classrooms",
        verbose_name="ساختمان",
    )

    class Meta:
        verbose_name = "کلاس"
        verbose_name_plural = "کلاس‌ها"

    def __str__(self):
        return f"{self.title} ({self.building.title})"
