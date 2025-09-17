# یونی‌شدول

## معرفی پروژه
یونی‌شدول یک پروژهٔ جنگو برای مدیریت برنامه‌ریزی دانشگاهی است که شامل اپ‌های مختلف برای حساب‌های کاربری، دوره‌ها، زمان‌بندی کلاس‌ها و سایر اجزای مرتبط می‌باشد.

## پیش‌نیازها
- Python 3.10 یا بالاتر
- pip و virtualenv برای ایجاد محیط مجازی
- پایگاه دادهٔ SQLite (به صورت پیش‌فرض استفاده می‌شود)

## نصب و اجرای سرور
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## ساختار اپ‌ها
پروژه شامل اپ‌های زیر است:
- `accounts`: مدیریت کاربران و احراز هویت
- `courses`: اطلاعات مربوط به دروس
- `institutions`: نهادها و دانشکده‌ها
- `locations`: مکان‌ها و کلاس‌ها
- `professors`: اساتید و اطلاعات مربوطه
- `schedules`: مدیریت برنامه‌های درسی
- `semesters`: ترم‌های تحصیلی
- `displays`: مدیریت نمایشگرهای عمومی و فیلترهای انتشار برنامه‌ها

## API نمایشگرها
برای مدیریت نمایشگرهای عمومی و فیلترهای مرتبط با آن‌ها می‌توانید از مسیرهای زیر استفاده کنید:

| متد | مسیر | توضیح |
| --- | --- | --- |
| `GET` | `/api/displays/screens/` | فهرست تمامی نمایشگرهای مؤسسه‌ی کاربر |
| `POST` | `/api/displays/screens/create/` | ایجاد نمایشگر جدید با عنوان، تم و فاصله‌ی تازه‌سازی |
| `GET` | `/api/displays/screens/<id>/` | دریافت جزئیات نمایشگر خاص |
| `PUT` | `/api/displays/screens/<id>/update/` | ویرایش نمایشگر |
| `DELETE` | `/api/displays/screens/<id>/delete/` | حذف (نرم) نمایشگر |
| `GET` | `/api/displays/screens/<id>/filters/` | فهرست فیلترهای یک نمایشگر |
| `POST` | `/api/displays/screens/<id>/filters/create/` | ایجاد فیلتر جدید برای نمایشگر |
| `PUT` | `/api/displays/filters/<id>/update/` | ویرایش فیلتر |
| `DELETE` | `/api/displays/filters/<id>/delete/` | حذف فیلتر |

نمایش عمومی هر نمایشگر از مسیر `/displays/<slug>/` قابل دسترس است. در صورت ارسال پارامتر `?format=html`، قالب HTML همراه با به‌روزرسانی خودکار و پیام‌های نوار اطلاع‌رسانی ارائه می‌شود؛ در حالت پیش‌فرض خروجی JSON با ساختار استاندارد `BaseResponse` بازگردانده خواهد شد.

## مستندات بیشتر
برای آشنایی با API و نمونه درخواست‌ها می‌توانید به فایل [Unischedule API.postman_collection.json](Unischedule%20API.postman_collection.json) مراجعه کنید.
