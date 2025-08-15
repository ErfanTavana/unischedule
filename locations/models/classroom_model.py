from django.db import models
from unischedule.core.base_model import BaseModel
from locations.models import Building

class Classroom(BaseModel):
    """
    Represents a physical classroom within a building (e.g., کلاس ۱۰۱، آزمایشگاه کامپیوتر).
    """

    title = models.CharField(max_length=100, help_text="مثلاً کلاس ۱۰۱ یا آزمایشگاه شبکه")
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="classrooms")

    class Meta:
        verbose_name = "Classroom"
        verbose_name_plural = "Classrooms"

    def __str__(self):
        return f"{self.title} ({self.building.title})"
