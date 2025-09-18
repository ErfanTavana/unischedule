from __future__ import annotations

import secrets
from datetime import datetime
from typing import Dict

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from unischedule.core.base_model import BaseModel
from institutions.models import Institution
from locations.models import Classroom
from professors.models import Professor
from courses.models import Course
from semesters.models import Semester
from schedules.models import ClassSession

# Mapping Python's weekday index to the Persian choices used in ClassSession
PY_WEEKDAY_TO_PERSIAN: Dict[int, str] = {
    5: "شنبه",
    6: "یکشنبه",
    0: "دوشنبه",
    1: "سه‌شنبه",
    2: "چهارشنبه",
    3: "پنجشنبه",
    4: "جمعه",
}


class DisplayScreen(BaseModel):
    """Public-facing playlist grouping for one or more display filters."""

    class LayoutTheme(models.TextChoices):
        DEFAULT = "default", "پیش‌فرض"
        DARK = "dark", "تیره"
        LIGHT = "light", "روشن"

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="display_screens",
        verbose_name="مؤسسه",
    )
    title = models.CharField(max_length=255, verbose_name="عنوان")
    slug = models.SlugField(max_length=64, unique=True, blank=True, verbose_name="شناسه عمومی")
    access_token = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        null=True,
        verbose_name="توکن دسترسی",
    )
    refresh_interval = models.PositiveIntegerField(
        default=60,
        help_text="بازه تازه‌سازی (ثانیه)",
        verbose_name="بازه تازه‌سازی",
    )
    layout_theme = models.CharField(
        max_length=20,
        choices=LayoutTheme.choices,
        default=LayoutTheme.DEFAULT,
        verbose_name="قالب نمایش",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال است؟")

    class Meta:
        verbose_name = "صفحه نمایش"
        verbose_name_plural = "صفحات نمایش"
        ordering = ("title",)

    def __str__(self) -> str:  # pragma: no cover - simple string representation
        return f"{self.title} ({self.institution.name})"

    def clean(self):
        super().clean()
        if self.refresh_interval <= 0:
            raise ValidationError({"refresh_interval": "بازه تازه‌سازی باید عددی مثبت باشد."})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or secrets.token_hex(4)
            slug_candidate = base_slug
            counter = 1
            while type(self).objects_with_deleted.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
                slug_candidate = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug_candidate
        if not self.access_token:
            self.access_token = secrets.token_urlsafe(16)
        self.full_clean()
        super().save(*args, **kwargs)


class DisplayFilter(BaseModel):
    """Holds filtering configuration for a display screen playlist item."""

    display_screen = models.ForeignKey(
        DisplayScreen,
        on_delete=models.CASCADE,
        related_name="filters",
        verbose_name="صفحه نمایش",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="عنوان اختیاری",
        help_text="برای تفکیک راحت‌تر فیلترها در مدیریت.",
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        related_name="display_filters",
        blank=True,
        null=True,
        verbose_name="کلاس",
    )
    professor = models.ForeignKey(
        Professor,
        on_delete=models.SET_NULL,
        related_name="display_filters",
        blank=True,
        null=True,
        verbose_name="استاد",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        related_name="display_filters",
        blank=True,
        null=True,
        verbose_name="درس",
    )
    semester = models.ForeignKey(
        Semester,
        on_delete=models.SET_NULL,
        related_name="display_filters",
        blank=True,
        null=True,
        verbose_name="ترم",
    )
    day_of_week = models.CharField(
        max_length=20,
        choices=ClassSession.DAY_OF_WEEK_CHOICES,
        blank=True,
        null=True,
        verbose_name="روز هفته",
    )
    week_type = models.CharField(
        max_length=20,
        choices=ClassSession.WeekTypeChoices.choices,
        blank=True,
        null=True,
        verbose_name="نوع هفته",
    )
    date_override = models.DateField(
        blank=True,
        null=True,
        verbose_name="تاریخ دلخواه",
        help_text="در صورت تعیین، روز و نوع هفته بر اساس این تاریخ محاسبه می‌شود.",
    )
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
        help_text="ترتیب نمایش در پلن صفحه.",
    )
    duration_seconds = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="مدت نمایش",
        help_text="در صورت چرخش بین چند فیلتر، مدت نمایش این فیلتر.",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال است؟")

    class Meta:
        verbose_name = "فیلتر نمایش"
        verbose_name_plural = "فیلترهای نمایش"
        ordering = ("position", "id")

    def __str__(self) -> str:  # pragma: no cover - simple string representation
        return self.title or f"Filter #{self.pk} for {self.display_screen.title}"

    def clean(self):
        super().clean()
        selectors = [
            self.classroom,
            self.professor,
            self.course,
            self.semester,
            self.day_of_week,
            self.week_type,
            self.date_override,
        ]
        if not any(selectors):
            raise ValidationError("حداقل یکی از معیارهای فیلتر باید مشخص شود.")

        if not self.display_screen_id:
            return

        institution = self.display_screen.institution
        errors = {}
        if self.classroom and self.classroom.building.institution != institution:
            errors["classroom"] = "کلاس انتخاب‌شده متعلق به این مؤسسه نیست."
        if self.professor and self.professor.institution != institution:
            errors["professor"] = "استاد انتخاب‌شده متعلق به این مؤسسه نیست."
        if self.course and self.course.institution != institution:
            errors["course"] = "درس انتخاب‌شده متعلق به این مؤسسه نیست."
        if self.semester and self.semester.institution != institution:
            errors["semester"] = "ترم انتخاب‌شده متعلق به این مؤسسه نیست."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def computed_day_of_week(self) -> str | None:
        if self.day_of_week:
            return self.day_of_week
        if self.date_override:
            return PY_WEEKDAY_TO_PERSIAN.get(self.date_override.weekday())
        return None

    @property
    def computed_week_type(self) -> str | None:
        if self.week_type:
            return self.week_type
        if self.date_override:
            week_number = self.date_override.isocalendar()[1]
            return (
                ClassSession.WeekTypeChoices.ODD
                if week_number % 2
                else ClassSession.WeekTypeChoices.EVEN
            )
        return None


class DisplayMessage(BaseModel):
    """Optional ticker/alert messages for a display screen."""

    display_screen = models.ForeignKey(
        DisplayScreen,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="صفحه نمایش",
    )
    content = models.TextField(verbose_name="پیام")
    is_active = models.BooleanField(default=True, verbose_name="فعال است؟")
    priority = models.IntegerField(default=0, verbose_name="اولویت")
    starts_at = models.DateTimeField(blank=True, null=True, verbose_name="شروع نمایش")
    ends_at = models.DateTimeField(blank=True, null=True, verbose_name="پایان نمایش")

    class Meta:
        verbose_name = "پیام نمایش"
        verbose_name_plural = "پیام‌های نمایش"
        ordering = ("-priority", "created_at")

    def __str__(self) -> str:  # pragma: no cover - simple string representation
        return self.content[:50]

    def is_visible(self, reference: datetime | None = None) -> bool:
        now = reference or timezone.now()
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        return self.is_active
