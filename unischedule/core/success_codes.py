"""Shared application success codes grouped by domain.

The codes follow a ``2XYZ`` convention where the second digit indicates the
domain (e.g. ``8`` for institutions, ``1`` for semesters). Grouping the codes
here helps product and client teams maintain a single source of truth when
mapping server responses to UI messages.

Example:
    ``BaseResponse.success(**SuccessCodes.INSTITUTION_CREATED)`` turns the
    constant into the standard response format without duplicating the message
    at the call site.
"""


class SuccessCodes:
    """Namespace containing grouped dictionaries used by ``BaseResponse``."""

    # Institutions: all institution management scenarios share the 28xx range.
    INSTITUTION_LISTED = {
        "code": "2800",
        "message": "لیست مؤسسات با موفقیت دریافت شد.",
        "data": {},
    }
    INSTITUTION_RETRIEVED = {
        "code": "2801",
        "message": "اطلاعات مؤسسه با موفقیت دریافت شد.",
        "data": {},
    }
    INSTITUTION_CREATED = {
        "code": "2802",
        "message": "مؤسسه جدید با موفقیت ایجاد شد.",
        "data": {},
    }
    INSTITUTION_UPDATED = {
        "code": "2803",
        "message": "اطلاعات مؤسسه با موفقیت به‌روزرسانی شد.",
        "data": {},
    }
    INSTITUTION_DELETED = {
        "code": "2804",
        "message": "مؤسسه با موفقیت حذف شد.",
        "data": {},
    }

    # Semesters: the 21xx series communicates academic term lifecycle events.
    SEMESTER_CREATED = {
        "code": "2100",
        "message": "ترم با موفقیت ایجاد شد.",
        "data": {}
    }

    SEMESTER_LISTED = {
        "code": "2101",
        "message": "لیست ترم‌ها با موفقیت دریافت شد.",
        "data": {}
    }

    SEMESTER_UPDATED = {
        "code": "2102",
        "message": "ترم با موفقیت بروزرسانی شد.",
        "data": {}
    }

    SEMESTER_DELETED = {
        "code": "2103",
        "message": "ترم با موفقیت حذف شد.",
        "data": {}
    }

    SEMESTER_SET_ACTIVE = {
        "code": "2104",
        "message": "ترم فعال با موفقیت تنظیم شد.",
        "data": {}
    }

    # Professors: 22xx codes mirror CRUD operations on faculty profiles.
    PROFESSOR_LISTED = {
        "code": "2201",
        "message": "لیست اساتید با موفقیت دریافت شد.",
        "data": {}
    }

    PROFESSOR_RETRIEVED = {
        "code": "2202",
        "message": "اطلاعات استاد با موفقیت دریافت شد.",
        "data": {}
    }

    PROFESSOR_CREATED = {
        "code": "2203",
        "message": "استاد با موفقیت ایجاد شد.",
        "data": {}
    }

    PROFESSOR_UPDATED = {
        "code": "2204",
        "message": "اطلاعات استاد با موفقیت به‌روزرسانی شد.",
        "data": {}
    }

    PROFESSOR_DELETED = {
        "code": "2205",
        "message": "استاد با موفقیت حذف شد.",
        "data": {}
    }

    # Courses: 23xx indicates catalog level changes and queries.
    COURSE_CREATED = {
        "code": "2301",
        "message": "درس جدید با موفقیت ایجاد شد.",
        "data": {}
    }

    COURSE_LISTED = {
        "code": "2302",
        "message": "لیست دروس با موفقیت دریافت شد.",
        "data": {}
    }

    COURSE_RETRIEVED = {
        "code": "2303",
        "message": "اطلاعات درس با موفقیت دریافت شد.",
        "data": {}
    }

    COURSE_UPDATED = {
        "code": "2304",
        "message": "اطلاعات درس با موفقیت به‌روزرسانی شد.",
        "data": {}
    }

    COURSE_DELETED = {
        "code": "2305",
        "message": "درس با موفقیت حذف شد.",
        "data": {}
    }

    # Buildings: facility management uses 24xx aligned with location entities.
    BUILDING_CREATED = {
        "code": "2401",
        "message": "ساختمان با موفقیت ایجاد شد."
    }
    BUILDING_RETRIEVED = {
        "code": "2402",
        "message": "اطلاعات ساختمان با موفقیت دریافت شد."
    }
    BUILDING_UPDATED = {
        "code": "2403",
        "message": "اطلاعات ساختمان با موفقیت به‌روزرسانی شد."
    }
    BUILDING_DELETED = {
        "code": "2404",
        "message": "ساختمان با موفقیت حذف شد."
    }
    BUILDING_LISTED = {
        "code": "2405",
        "message": "لیست ساختمان‌ها با موفقیت دریافت شد."
    }

    # Classrooms: 25xx signals updates to physical classroom resources.
    CLASSROOM_LISTED = {
        "code": "2501",
        "message": "لیست کلاس‌ها با موفقیت دریافت شد."
    }

    CLASSROOM_RETRIEVED = {
        "code": "2502",
        "message": "اطلاعات کلاس با موفقیت دریافت شد."
    }

    CLASSROOM_CREATED = {
        "code": "2503",
        "message": "کلاس جدید با موفقیت ایجاد شد."
    }

    CLASSROOM_UPDATED = {
        "code": "2504",
        "message": "اطلاعات کلاس با موفقیت به‌روزرسانی شد."
    }

    CLASSROOM_DELETED = {
        "code": "2505",
        "message": "کلاس با موفقیت حذف شد."
    }

    # Class Sessions: 26xx maps to scheduling occurrences inside semesters.
    CLASS_SESSION_CREATED = {
        "code": "2601",
        "message": "جلسه کلاس با موفقیت ایجاد شد.",
        "data": {},
    }
    CLASS_SESSION_LISTED = {
        "code": "2602",
        "message": "لیست جلسات کلاس با موفقیت دریافت شد.",
        "data": {},
    }
    CLASS_SESSION_RETRIEVED = {
        "code": "2603",
        "message": "اطلاعات جلسه کلاس با موفقیت دریافت شد.",
        "data": {},
    }
    CLASS_SESSION_UPDATED = {
        "code": "2604",
        "message": "جلسه کلاس با موفقیت به‌روزرسانی شد.",
        "data": {},
    }
    CLASS_SESSION_DELETED = {
        "code": "2605",
        "message": "جلسه کلاس با موفقیت حذف شد.",
        "data": {},
    }

    # Display screens: 27xx is dedicated to digital signage endpoints.
    DISPLAY_SCREEN_CREATED = {
        "code": "2701",
        "message": "صفحه نمایش با موفقیت ایجاد شد.",
        "data": {},
    }
    DISPLAY_SCREEN_LISTED = {
        "code": "2702",
        "message": "لیست صفحات نمایش با موفقیت دریافت شد.",
        "data": {},
    }
    DISPLAY_SCREEN_RETRIEVED = {
        "code": "2703",
        "message": "صفحه نمایش با موفقیت دریافت شد.",
        "data": {},
    }
    DISPLAY_SCREEN_UPDATED = {
        "code": "2704",
        "message": "صفحه نمایش با موفقیت به‌روزرسانی شد.",
        "data": {},
    }
    DISPLAY_SCREEN_DELETED = {
        "code": "2705",
        "message": "صفحه نمایش با موفقیت حذف شد.",
        "data": {},
    }
    DISPLAY_SCREEN_RENDERED = {
        "code": "2790",
        "message": "اطلاعات صفحه نمایش با موفقیت بارگذاری شد.",
        "data": {},
    }

    # ✅ Auth: success codes used by authentication flows.
    LOGIN_SUCCESS = {
        "code": 2001,
        "message": "ورود با موفقیت انجام شد.",
    }
    LOGOUT_SUCCESS = {
        "code": 2201,
        "message": "خروج از حساب با موفقیت انجام شد."
    }
    PASSWORD_CHANGE_SUCCESS = {
        "code": 2002,
        "message": "رمز عبور با موفقیت تغییر کرد.",
        "data": {},
    }
