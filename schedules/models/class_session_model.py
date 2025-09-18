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
        EVERY = "هرهفته", "هرهفته"
        ODD = "فرد", "فرد"
        EVEN = "زوج", "زوج"

    DAY_OF_WEEK_CHOICES = [
        ("شنبه", "شنبه"),
        ("یکشنبه", "یکشنبه"),
        ("دوشنبه", "دوشنبه"),
        ("سه‌شنبه", "سه‌شنبه"),
        ("چهارشنبه", "چهارشنبه"),
        ("پنجشنبه", "پنجشنبه"),
        ("جمعه", "جمعه"),
    ]

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="class_sessions",
        verbose_name="مؤسسه",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="class_sessions",
        verbose_name="درس",
    )
    professor = models.ForeignKey(
        Professor,
        on_delete=models.CASCADE,
        related_name="class_sessions",
        verbose_name="استاد",
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="class_sessions",
        verbose_name="کلاس",
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.CASCADE,
        related_name="class_sessions",
        verbose_name="ترم",
    )

    day_of_week = models.CharField(max_length=10, choices=DAY_OF_WEEK_CHOICES, verbose_name="روز هفته")
    start_time = models.TimeField(verbose_name="زمان شروع")
    end_time = models.TimeField(verbose_name="زمان پایان")

    week_type = models.CharField(
        max_length=15,
        choices=WeekTypeChoices.choices,
        default=WeekTypeChoices.EVERY,
        verbose_name="نوع هفته",
    )
    group_code = models.CharField(max_length=50, blank=True, null=True, verbose_name="کد گروه")
    capacity = models.PositiveIntegerField(default=0, verbose_name="ظرفیت")
    note = models.TextField(blank=True, null=True, verbose_name="یادداشت")

    class Meta:
        verbose_name = "جلسه کلاس"
        verbose_name_plural = "جلسات کلاس"

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.course.title} - {self.day_of_week}" 
