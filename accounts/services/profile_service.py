"""Profile-centric service utilities for authenticated account operations.

This module exposes thin wrappers around institution-aware media helpers so
the accounts application can interact with profile assets (such as the logo)
without needing to know implementation details about the institutions app.
All public functions accept the authenticated ``User`` instance to ensure
access control and multi-tenancy checks are performed consistently.
"""

from institutions.services import (
    get_institution_logo,
    update_institution_logo,
    delete_institution_logo,
)


def get_authenticated_institution_logo(user, *, context: dict | None = None) -> dict:
    """لوگوی مؤسسه کاربر احراز هویت شده را بازیابی می‌کند.

    Args:
        user: شیء ``User`` لاگین کرده که انتظار می‌رود به یک مؤسسه متصل باشد.
        context: دیکشنری اختیاری برای عبور تنظیمات اضافی به سریالایزر پایین‌دستی.

    Returns:
        dict: خروجی سریال‌شده‌ای که توسط خدمات مؤسسه تولید می‌شود و شامل متادیتای
        فایل است.

    Raises:
        CustomValidationError: زمانی که کاربر به مؤسسه‌ای متصل نباشد یا سرویس
        مؤسسه محدودیت‌های دامنه‌ای را نقض شده تشخیص دهد.
    """

    institution = getattr(user, "institution", None)
    return get_institution_logo(institution, context=context)


def update_authenticated_institution_logo(
    user,
    data: dict,
    *,
    context: dict | None = None,
) -> dict:
    """لوگوی مؤسسه مرتبط با کاربر را با فایل جدید جایگزین می‌کند.

    Args:
        user: نمونه‌ی کاربر احراز هویت شده.
        data: دیکشنری حاوی داده‌های فرم، معمولاً شامل فایل بارگذاری شده.
        context: تنظیمات اختیاری برای عبور به سریالایزر مؤسسه.

    Returns:
        dict: خروجی سریال‌شده از سرویس مؤسسه پس از به‌روزرسانی موفق.

    Raises:
        CustomValidationError: اگر اعتبارسنجی داده‌های ورودی شکست بخورد یا لوگو با
        قوانین کسب‌وکار تعیین‌شده سازگار نباشد.
    """

    institution = getattr(user, "institution", None)
    return update_institution_logo(institution, data, context=context)


def delete_authenticated_institution_logo(user, *, context: dict | None = None) -> dict:
    """لوگوی مؤسسه متصل به کاربر را حذف و متادیتای به‌روز شده را باز می‌گرداند.

    Args:
        user: کاربر احراز هویت شده‌ای که می‌خواهد لوگو را حذف کند.
        context: پارامترهای اختیاری برای سفارشی‌سازی خروجی سریالایزر.

    Returns:
        dict: متادیتای جدید لوگو (معمولاً مقادیر تهی) پس از حذف موفق.

    Raises:
        CustomValidationError: اگر کاربر مؤسسه معتبری نداشته باشد یا عملیات حذف در
        سرویس مؤسسه با شکست مواجه شود.
    """

    institution = getattr(user, "institution", None)
    return delete_institution_logo(institution, context=context)
