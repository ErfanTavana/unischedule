"""Central repository of error codes referenced by API responses.

Error codes use the ``4XYZ`` family so they are easy to distinguish from
success codes. The second digit hints at the domain: ``9`` for institutions,
``1`` for semesters, etc. This convention keeps HTTP codes, logical codes and
user-facing messages together, which simplifies raising errors through
``BaseResponse.error`` or :class:`~unischedule.core.exceptions.CustomValidationError`.

Example:
    ``BaseResponse.error(**ErrorCodes.SEMESTER_NOT_FOUND)`` immediately returns
    an HTTP 404 without redefining the message or application code.
"""

from rest_framework import status


class ErrorCodes:
    """Domain grouped error payloads shared across serializers and services."""

    # Generic: 40xx codes cover validation and permission scenarios.
    VALIDATION_FAILED = {
        "code": "4000",
        "message": "اطلاعات وارد شده نامعتبر است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    INSTITUTION_REQUIRED = {
        "code": "4001",
        "message": "برای انجام این عملیات، کاربر باید به یک مؤسسه متصل باشد.",
        "status_code": status.HTTP_403_FORBIDDEN,
        "errors": [],
        "data": {},
    }

    # Institution: 49xx codes represent issues when managing institutions.
    INSTITUTION_NOT_FOUND = {
        "code": "4900",
        "message": "مؤسسه مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    INSTITUTION_DUPLICATE_SLUG = {
        "code": "4901",
        "message": "نامک وارد شده قبلاً استفاده شده است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    INSTITUTION_CREATION_FAILED = {
        "code": "4902",
        "message": "ایجاد مؤسسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    INSTITUTION_UPDATE_FAILED = {
        "code": "4903",
        "message": "به‌روزرسانی اطلاعات مؤسسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    INSTITUTION_DELETION_FAILED = {
        "code": "4904",
        "message": "حذف مؤسسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    INSTITUTION_LOGO_RETRIEVE_FAILED = {
        "code": "4905",
        "message": "دریافت لوگوی مؤسسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    INSTITUTION_LOGO_UPDATE_FAILED = {
        "code": "4906",
        "message": "به‌روزرسانی لوگوی مؤسسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    INSTITUTION_LOGO_DELETE_FAILED = {
        "code": "4907",
        "message": "حذف لوگوی مؤسسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }

    # Semester: 41xx warnings communicate failures on academic terms.
    SEMESTER_NOT_FOUND = {
        "code": "4100",
        "message": "ترم مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    SEMESTER_CREATION_FAILED = {
        "code": "4101",
        "message": "ایجاد ترم با خطا مواجه شد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    SEMESTER_UPDATE_FAILED = {
        "code": "4102",
        "message": "ویرایش ترم با خطا مواجه شد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    SEMESTER_DELETE_FAILED = {
        "code": "4103",
        "message": "حذف ترم با خطا مواجه شد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    SEMESTER_ALREADY_ACTIVE = {
        "code": "4104",
        "message": "ترم انتخاب‌شده هم‌اکنون فعال است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }

    # Professor: 42xx handles CRUD exceptions around faculty members.
    PROFESSOR_NOT_FOUND = {
        "code": "4200",
        "message": "استاد مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    PROFESSOR_CREATION_FAILED = {
        "code": "4201",
        "message": "ایجاد استاد با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    PROFESSOR_UPDATE_FAILED = {
        "code": "4202",
        "message": "به‌روزرسانی اطلاعات استاد با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    PROFESSOR_DELETION_FAILED = {
        "code": "4203",
        "message": "حذف استاد با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }

    # Course: 43xx focuses on catalog validation and persistence issues.
    COURSE_CREATION_FAILED = {
        "code": "4301",
        "message": "ایجاد درس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    COURSE_UPDATE_FAILED = {
        "code": "4302",
        "message": "به‌روزرسانی اطلاعات درس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    COURSE_DELETION_FAILED = {
        "code": "4303",
        "message": "حذف درس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    COURSE_NOT_FOUND = {
        "code": "4304",
        "message": "درس مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    COURSE_VALIDATION_FAILED = {
        "code": "4305",
        "message": "اطلاعات وارد شده نامعتبر است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }

    # Building: 44xx is reserved for facility management failures.
    BUILDING_NOT_FOUND = {
        "code": "4400",
        "message": "ساختمان مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    BUILDING_CREATION_FAILED = {
        "code": "4401",
        "message": "ایجاد ساختمان با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    BUILDING_UPDATE_FAILED = {
        "code": "4402",
        "message": "به‌روزرسانی اطلاعات ساختمان با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    BUILDING_DELETION_FAILED = {
        "code": "4403",
        "message": "حذف ساختمان با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }

    # Classroom: 45xx highlights classroom lifecycle problems.
    CLASSROOM_NOT_FOUND = {
        "code": "4500",
        "message": "کلاس مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    CLASSROOM_CREATION_FAILED = {
        "code": "4501",
        "message": "ایجاد کلاس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    CLASSROOM_UPDATE_FAILED = {
        "code": "4502",
        "message": "به‌روزرسانی اطلاعات کلاس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    CLASSROOM_DELETION_FAILED = {
        "code": "4503",
        "message": "حذف کلاس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }

    # Class Session: 46xx represents scheduling conflicts or errors.
    CLASS_SESSION_NOT_FOUND = {
        "code": "4600",
        "message": "جلسه کلاس مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    CLASS_SESSION_CONFLICT = {
        "code": "4601",
        "message": "تداخل در زمان یا مکان کلاس وجود دارد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    CLASS_SESSION_CREATION_FAILED = {
        "code": "4602",
        "message": "ایجاد جلسه کلاس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    CLASS_SESSION_UPDATE_FAILED = {
        "code": "4603",
        "message": "به‌روزرسانی جلسه کلاس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    CLASS_SESSION_DELETION_FAILED = {
        "code": "4604",
        "message": "حذف جلسه کلاس با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    CLASS_CANCELLATION_NOT_FOUND = {
        "code": "4605",
        "message": "لغو جلسه مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    CLASS_CANCELLATION_CONFLICT = {
        "code": "4606",
        "message": "برای این تاریخ قبلاً لغو ثبت شده است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    CLASS_CANCELLATION_DATE_MISMATCH = {
        "code": "4612",
        "message": "تاریخ انتخابی با برنامه کلاس همخوانی ندارد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    CLASS_CANCELLATION_CREATION_FAILED = {
        "code": "4607",
        "message": "ثبت لغو جلسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    CLASS_CANCELLATION_UPDATE_FAILED = {
        "code": "4608",
        "message": "به‌روزرسانی لغو جلسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    CLASS_CANCELLATION_DELETION_FAILED = {
        "code": "4609",
        "message": "حذف لغو جلسه با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    MAKEUP_SESSION_NOT_FOUND = {
        "code": "4610",
        "message": "جلسه جبرانی مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    MAKEUP_SESSION_CONFLICT = {
        "code": "4611",
        "message": "زمان جلسه جبرانی با برنامه‌های دیگر تداخل دارد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {},
    }
    MAKEUP_SESSION_CREATION_FAILED = {
        "code": "4612",
        "message": "ایجاد جلسه جبرانی با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    MAKEUP_SESSION_UPDATE_FAILED = {
        "code": "4613",
        "message": "به‌روزرسانی جلسه جبرانی با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    MAKEUP_SESSION_DELETION_FAILED = {
        "code": "4614",
        "message": "حذف جلسه جبرانی با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }

    # Display screens: 48xx is dedicated to signage endpoints.
    DISPLAY_SCREEN_NOT_FOUND = {
        "code": "4800",
        "message": "صفحه نمایش مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    DISPLAY_SCREEN_CREATION_FAILED = {
        "code": "4801",
        "message": "ایجاد صفحه نمایش با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    DISPLAY_SCREEN_UPDATE_FAILED = {
        "code": "4802",
        "message": "به‌روزرسانی صفحه نمایش با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    DISPLAY_SCREEN_DELETION_FAILED = {
        "code": "4803",
        "message": "حذف صفحه نمایش با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }

    # Auth: 47xx concentrates on authentication and security workflows.
    INVALID_CREDENTIALS = {
        "code": "4700",
        "message": "نام کاربری یا رمز عبور اشتباه است.",
        "status_code": status.HTTP_401_UNAUTHORIZED,
        "errors": ["Invalid username or password."],
        "data": {},
    }
    LOGIN_FAILED = {
        "code": "4701",
        "message": "ورود با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": ["Login failed due to a server error."],
        "data": {},
    }
    TOKEN_NOT_FOUND = {
        "code": "4702",
        "message": "توکن کاربر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {},
    }
    LOGOUT_FAILED = {
        "code": "4703",
        "message": "خروج از حساب با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
    PASSWORD_INCORRECT = {
        "code": "4704",
        "message": "رمز عبور فعلی نادرست است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": ["The current password provided is incorrect."],
        "data": {},
    }
    PASSWORD_CHANGE_FAILED = {
        "code": "4705",
        "message": "تغییر رمز عبور با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {},
    }
