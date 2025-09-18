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
    filters = models.JSONField(
        default=list,
        blank=True,
        verbose_name="پیکربندی فیلترها",
        help_text="تعریف فیلترهای صفحه به‌صورت ساختار یافته.",
    )

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
