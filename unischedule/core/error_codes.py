from rest_framework import status


class ErrorCodes:
    SEMESTER_NOT_FOUND = {
        "code": "4100",
        "message": "ترم مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {}
    }

    SEMESTER_CREATION_FAILED = {
        "code": "4101",
        "message": "ایجاد ترم با خطا مواجه شد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }
    VALIDATION_FAILED = {
        "code": "4102",
        "message": "اطلاعات وارد شده نامعتبر است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    SEMESTER_UPDATE_FAILED = {
        "code": "4102",
        "message": "ویرایش ترم با خطا مواجه شد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    SEMESTER_DELETE_FAILED = {
        "code": "4103",
        "message": "حذف ترم با خطا مواجه شد.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }

    SEMESTER_ALREADY_ACTIVE = {
        "code": "4104",
        "message": "ترم انتخاب‌شده هم‌اکنون فعال است.",
        "status_code": status.HTTP_400_BAD_REQUEST,
        "errors": [],
        "data": {}
    }
    PROFESSOR_NOT_FOUND = {
        "code": "4200",
        "message": "استاد مورد نظر یافت نشد.",
        "status_code": status.HTTP_404_NOT_FOUND,
        "errors": [],
        "data": {}
    }

    PROFESSOR_CREATION_FAILED = {
        "code": "4201",
        "message": "ایجاد استاد با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {}
    }

    PROFESSOR_UPDATE_FAILED = {
        "code": "4202",
        "message": "به‌روزرسانی اطلاعات استاد با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {}
    }

    PROFESSOR_DELETION_FAILED = {
        "code": "4203",
        "message": "حذف استاد با خطا مواجه شد.",
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "errors": [],
        "data": {}
    }
    # === COURSE ===
    COURSE_CREATION_FAILED = {
        "code": "4301",
        "message": "ایجاد درس با خطا مواجه شد.",
        "status_code": 500,
        "errors": [],
        "data": {}
    }

    COURSE_UPDATE_FAILED = {
        "code": "4302",
        "message": "به‌روزرسانی اطلاعات درس با خطا مواجه شد.",
        "status_code": 500,
        "errors": [],
        "data": {}
    }

    COURSE_DELETION_FAILED = {
        "code": "4303",
        "message": "حذف درس با خطا مواجه شد.",
        "status_code": 500,
        "errors": [],
        "data": {}
    }

    COURSE_NOT_FOUND = {
        "code": "4304",
        "message": "درس مورد نظر یافت نشد.",
        "status_code": 404,
        "errors": [],
        "data": {}
    }

    COURSE_VALIDATION_FAILED = {
        "code": "4305",
        "message": "اطلاعات وارد شده نامعتبر است.",
        "status_code": 400,
        "errors": [],
        "data": {}
    }

    # Buildings
    BUILDING_NOT_FOUND = {
        "code": "4100",
        "message": "ساختمان مورد نظر یافت نشد.",
        "status_code": 404,
        "errors": []
    }
    BUILDING_CREATION_FAILED = {
        "code": "4401",
        "message": "ایجاد ساختمان با خطا مواجه شد.",
        "status_code": 500,
        "errors": []
    }
    BUILDING_UPDATE_FAILED = {
        "code": "4402",
        "message": "به‌روزرسانی اطلاعات ساختمان با خطا مواجه شد.",
        "status_code": 500,
        "errors": []
    }
    BUILDING_DELETION_FAILED = {
        "code": "4403",
        "message": "حذف ساختمان با خطا مواجه شد.",
        "status_code": 500,
        "errors": []
    }

    # --------- Classroom Error Codes ---------
    CLASSROOM_NOT_FOUND = {
        "code": "4100",
        "message": "کلاس مورد نظر یافت نشد.",
        "status_code": 404,
        "errors": []
    }

    CLASSROOM_CREATION_FAILED = {
        "code": "4501",
        "message": "ایجاد کلاس با خطا مواجه شد.",
        "status_code": 500,
        "errors": []
    }

    CLASSROOM_UPDATE_FAILED = {
        "code": "4502",
        "message": "به‌روزرسانی اطلاعات کلاس با خطا مواجه شد.",
        "status_code": 500,
        "errors": []
    }

    CLASSROOM_DELETION_FAILED = {
        "code": "4503",
        "message": "حذف کلاس با خطا مواجه شد.",
        "status_code": 500,
        "errors": []
    }

    # ✅ Auth
    INVALID_CREDENTIALS = {
        "code": 4101,
        "message": "نام کاربری یا رمز عبور اشتباه است.",
        "status_code": 401,
        "errors": ["Invalid username or password."]
    }

    LOGIN_FAILED = {
        "code": 4501,
        "message": "ورود با خطا مواجه شد.",
        "status_code": 500,
        "errors": ["Login failed due to a server error."]
    }

    TOKEN_NOT_FOUND = {
        "code": 4201,
        "message": "توکن کاربر یافت نشد.",
        "status_code": 404,
        "errors": [],
    }

    LOGOUT_FAILED = {
        "code": 4501,
        "message": "خروج از حساب با خطا مواجه شد.",
        "status_code": 500,
        "errors": [],
    }
