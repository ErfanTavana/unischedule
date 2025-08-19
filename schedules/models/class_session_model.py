from django.db import models
from unischedule.core.base_model import BaseModel
from institutions.models import Institution
from courses.models import Course
from professors.models import Professor
from locations.models import Classroom
from semesters.models import Semester


class ClassSession(BaseModel):
    """Represents a single scheduled class session."""

    class WeekTypeChoices(models.TextChoices):
        EVERY = "every", "هرهفته"
        ODD = "odd", "فرد"
        EVEN = "even", "زوج"

    DAY_OF_WEEK_CHOICES = [
        ("شنبه", "شنبه"),
        ("یکشنبه", "یکشنبه"),
        ("دوشنبه", "دوشنبه"),
        ("سه‌شنبه", "سه‌شنبه"),
        ("چهارشنبه", "چهارشنبه"),
        ("پنجشنبه", "پنجشنبه"),
        ("جمعه", "جمعه"),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="class_sessions")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="class_sessions")
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE, related_name="class_sessions")
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="class_sessions")
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="class_sessions")

    day_of_week = models.CharField(max_length=10, choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    week_type = models.CharField(max_length=5, choices=WeekTypeChoices.choices, default=WeekTypeChoices.EVERY)
    group_code = models.CharField(max_length=50, blank=True, null=True)
    capacity = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Class Session"
        verbose_name_plural = "Class Sessions"

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.course.title} - {self.day_of_week}" 
