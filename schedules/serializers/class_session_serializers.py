from rest_framework import serializers
from schedules.models import ClassSession


class ClassSessionSerializer(serializers.ModelSerializer):
    """سریالایزر عمومی برای نمایش جزئیات جلسهٔ کلاس."""

    class Meta:
        model = ClassSession
        fields = [
            "id",
            "institution",
            "course",
            "professor",
            "classroom",
            "semester",
            "day_of_week",
            "start_time",
            "end_time",
            "week_type",
            "group_code",
            "capacity",
            "note",
        ]


class CreateClassSessionSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد که ساختار فیلدهای روز/هفته و اعتبارسنجی زمان را تشریح می‌کند."""

    class Meta:
        model = ClassSession
        fields = [
            "course",
            "professor",
            "classroom",
            "semester",
            "day_of_week",
            "start_time",
            "end_time",
            "week_type",
            "group_code",
            "capacity",
            "note",
        ]

    def validate(self, attrs):
        """اطمینان می‌دهد زمان شروع قبل از پایان بوده و ترکیب روز/نوع هفته معتبر باشد."""
        # day_of_week و week_type به صورت مقادیر متنی انتخابی در مدل تعریف شده‌اند و
        # در سطح مدل توسط گزینه‌ها محدود می‌شوند؛ در اینجا تنها ترتیب زمانی بازه بررسی می‌شود.
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and start >= end:
            raise serializers.ValidationError("زمان شروع باید قبل از زمان پایان باشد.")
        return attrs


class UpdateClassSessionSerializer(serializers.ModelSerializer):
    """سریالایزر به‌روزرسانی که فیلدهای روز/نوع هفته را اختیاری کرده و منطق زمان را بازاستفاده می‌کند."""

    class Meta:
        model = ClassSession
        fields = [
            "course",
            "professor",
            "classroom",
            "semester",
            "day_of_week",
            "start_time",
            "end_time",
            "week_type",
            "group_code",
            "capacity",
            "note",
        ]
        extra_kwargs = {f: {"required": False} for f in fields}

    def validate(self, attrs):
        """در صورت ارسال هر دو مقدار زمان، ترتیب آن‌ها را برای جلوگیری از بازه معکوس بررسی می‌کند."""
        start = attrs.get("start_time")
        end = attrs.get("end_time")
        if start and end and start >= end:
            raise serializers.ValidationError("زمان شروع باید قبل از زمان پایان باشد.")
        return attrs
