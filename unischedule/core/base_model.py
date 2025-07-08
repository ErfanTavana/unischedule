from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """
    مدل پایه‌ای برای تمام مدل‌های پروژه، شامل فیلدهای متداول.
    """

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
