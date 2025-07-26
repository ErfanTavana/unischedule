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
