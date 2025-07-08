from rest_framework.exceptions import APIException


class CustomValidationError(APIException):
    """
    استثنای سفارشی برای مدیریت خطاهای منطقی یا اعتبارسنجی در لایه سرویس‌ها.

    این کلاس برای شرایطی مانند "OTP هنوز منقضی نشده" یا "ترم تکراری است" استفاده می‌شود و با DRF کاملاً سازگار است.
    """

    def __init__(
        self,
        message="خطایی رخ داده است.",
        code=2000,
        errors=None,
        status_code=400,
        data=None
    ):
        """
        Args:
            message (str): پیام اصلی خطا برای کاربر
            code (int): کد منطقی اپلیکیشن (مثلاً: 3001)
            errors (list): لیست خطاهای قابل نمایش (برای ولیدیشن یا توضیح بیشتر)
            status_code (int): کد HTTP مورد نظر برای پاسخ (مثل 400 یا 403)
            data (dict): اطلاعات اضافی مفید برای کلاینت (مثلاً زمان باقی‌مانده OTP)
        """
        self.detail = {
            "success": False,
            "message": message,
            "code": code,
            "errors": errors or [],
            "data": data or {}
        }
        self.status_code = status_code
