from rest_framework import status


class SuccessCodes:
    """
    کدها و پیام‌های موفقیت‌آمیز برای پاسخ‌های API
    """

    ACCOUNT_NOT_LOCKED = {
        "code": "2001",
        "message": "حساب کاربری قفل نمی‌باشد.",
        "data": {}
    }

    OTP_SENT_SUCCESSFULLY = {
        "code": "2002",
        "message": "کد تأیید با موفقیت ارسال شد.",
        "data": {}
    }

    SEMESTER_CREATED = {
        "code": "2003",
        "message": "ترم جدید با موفقیت ایجاد شد.",
        "data": {}
    }

    SCHEDULE_UPDATED = {
        "code": "2004",
        "message": "برنامه کلاسی با موفقیت بروزرسانی شد.",
        "data": {}
    }


class ErrorCodes:
    """
    کدها و پیام‌های خطا برای مدیریت یکپارچه پاسخ‌های ناموفق
    """

    # 🔹 خطاهای عمومی
    ERROR = {
        "code": "4000",
        "message": "خطای عمومی رخ داده است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    MISSING_REQUIRED_FIELDS = {
        "code": "4009",
        "message": "برخی از فیلدهای ضروری ارسال نشده‌اند.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    INVALID_REQUEST = {
        "code": "4010",
        "message": "درخواست نامعتبر است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    # 🔹 احراز هویت و کاربر
    INVALID_PHONE_NUMBER = {
        "code": "4001",
        "message": "شماره تلفن نامعتبر است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    USER_NOT_FOUND = {
        "code": "4006",
        "message": "کاربر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {}
    }

    AUTHENTICATION_FAILED = {
        "code": "4008",
        "message": "احراز هویت انجام نشد. لطفاً اطلاعات خود را بررسی کنید.",
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "errors": [],
        "data": {}
    }

    ACCOUNT_LOCKED = {
        "code": "4007",
        "message": "حساب شما به دلیل تلاش بیش از حد، موقتاً قفل شده است.",
        "status_code": status.HTTP_403_FORBIDDEN,
        "errors": [],
        "data": {}
    }

    # 🔹 OTP
    OTP_INVALID = {
        "code": "4002",
        "message": "کد تأیید معتبر نمی‌باشد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    OTP_EXPIRED = {
        "code": "4003",
        "message": "کد تأیید منقضی شده است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    OTP_NOT_EXPIRED = {
        "code": "4011",
        "message": "کد تأیید قبلی هنوز معتبر است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    OTP_ATTEMPT_LIMIT_EXCEEDED = {
        "code": "4004",
        "message": "تعداد تلاش‌های شما برای وارد کردن کد تأیید بیش از حد مجاز است.",
        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
        "errors": [],
        "data": {}
    }

    OTP_REQUEST_LIMIT_EXCEEDED = {
        "code": "4005",
        "message": "شما بیش از حد مجاز درخواست کد تأیید ارسال کرده‌اید.",
        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
        "errors": [],
        "data": {}
    }

    VERIFICATION_REQUEST_LIMIT_EXCEEDED = {
        "code": "4012",
        "message": "حد مجاز درخواست کد تأیید را رد کرده‌اید. لطفاً بعداً تلاش کنید.",
        "status_code": status.HTTP_429_TOO_MANY_REQUESTS,
        "errors": [],
        "data": {}
    }

    VERIFICATION_CODE_SENDING_FAILED = {
        "code": "4013",
        "message": "ارسال کد تأیید با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {}
    }

    PHONE_NUMBER_REQUIRED = {
        "code": "4014",
        "message": "شماره تلفن همراه الزامی است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": ["phone_number field is required."],
        "data": {}
    }

    # 🔹 ترم‌ها
    SEMESTER_ALREADY_EXISTS = {
        "code": "4100",
        "message": "ترمی با این عنوان قبلاً ثبت شده است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    NO_ACTIVE_SEMESTER = {
        "code": "4101",
        "message": "هیچ ترم فعالی وجود ندارد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {}
    }

    # 🔹 برنامه کلاسی
    SCHEDULE_CONFLICT = {
        "code": "4200",
        "message": "تداخل در برنامه کلاسی وجود دارد.",
        "status_code": status.HTTP_409_CONFLICT,
        "errors": [],
        "data": {}
    }

    SCHEDULE_NOT_FOUND = {
        "code": "4201",
        "message": "برنامه کلاسی مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {}
    }
