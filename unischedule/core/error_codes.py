from rest_framework import status


class ErrorCodes:
    # Generic
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

    # Institution
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

    # Semester
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

    # Professor
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

    # Course
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

    # Building
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

    # Classroom
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

    # Class Session
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

    # Display screens
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

    # Auth
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
