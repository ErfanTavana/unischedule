from __future__ import annotations

from django.db import models

from unischedule.core.base_model import BaseModel
from institutions.models import Institution
from locations.models import Classroom


class ClassCancellation(BaseModel):
    """Stores one-off cancellations for scheduled class sessions."""

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="class_cancellations",
        verbose_name="مؤسسه",
    )
    class_session = models.ForeignKey(
        "schedules.ClassSession",
        on_delete=models.CASCADE,
        related_name="cancellations",
        verbose_name="جلسه کلاس",
    )
    date = models.DateField(verbose_name="تاریخ لغو")
    reason = models.CharField(max_length=255, blank=True, verbose_name="دلیل")
    note = models.TextField(blank=True, verbose_name="یادداشت")

    class Meta:
        verbose_name = "لغو جلسه"
        verbose_name_plural = "لغو جلسات"
        ordering = ("-date", "-created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("class_session", "date"),
                condition=models.Q(is_deleted=False),
                name="unique_active_cancellation_per_session_and_date",
            )
        ]

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return f"لغو {self.class_session} در {self.date}"


class MakeupClassSession(BaseModel):
    """Represents a compensatory (makeup) occurrence for a class session."""

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="makeup_class_sessions",
        verbose_name="مؤسسه",
    )
    class_session = models.ForeignKey(
        "schedules.ClassSession",
        on_delete=models.CASCADE,
        related_name="makeup_sessions",
        verbose_name="جلسه مرجع",
    )
    date = models.DateField(verbose_name="تاریخ برگزاری")
    start_time = models.TimeField(verbose_name="زمان شروع")
    end_time = models.TimeField(verbose_name="زمان پایان")
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name="makeup_class_sessions",
        verbose_name="کلاس",
    )
    group_code = models.CharField(max_length=50, blank=True, verbose_name="کد گروه جایگزین")
    note = models.TextField(blank=True, verbose_name="یادداشت")

    class Meta:
        verbose_name = "جلسه جبرانی"
        verbose_name_plural = "جلسات جبرانی"
        ordering = ("date", "start_time")

    def __str__(self) -> str:  # pragma: no cover - debugging helper
        return f"جلسه جبرانی {self.class_session} در {self.date}"
