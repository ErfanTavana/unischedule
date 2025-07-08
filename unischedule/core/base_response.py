from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone


class DefaultPageNumberPagination(PageNumberPagination):
    """
    کلاس صفحه‌بندی پیش‌فرض برای پروژه.
    پارامتر page_size به‌صورت پویا از querystring قابل دریافت است.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class BaseResponse:
    """
    کلاس کمکی برای ساختن پاسخ‌های استاندارد API.
    """

    @staticmethod
    def success(
        message="عملیات موفقیت‌آمیز بود.",
        data=None,
        status_code=status.HTTP_200_OK,
        code=1000,
        warnings=None,
        meta=None
    ):
        """
        پاسخ موفق با ساختار استاندارد.

        Args:
            message (str): پیام موفقیت
            data (dict): داده خروجی
            status_code (int): کد HTTP
            code (int): کد منطقی اپلیکیشن
            warnings (list): هشدارهای غیر بحرانی
            meta (dict): متادیتای اضافی

        Returns:
            Response: پاسخ DRF استاندارد
        """
        return Response({
            "success": True,
            "code": code,
            "message": message,
            "data": data or {},
            "warnings": warnings or [],
            "meta": meta or {}
        }, status=status_code)

    @staticmethod
    def error(
        message="خطایی رخ داده است.",
        errors=None,
        status_code=status.HTTP_400_BAD_REQUEST,
        code=2000,
        data=None
    ):
        """
        پاسخ خطا با ساختار استاندارد.

        Args:
            message (str): پیام خطا
            errors (list): لیست خطاهای ولیدیشن یا منطقی
            status_code (int): کد HTTP
            code (int): کد منطقی اپلیکیشن
            data (dict): داده اضافی قابل نمایش

        Returns:
            Response: پاسخ DRF با ساختار استاندارد خطا
        """
        return Response({
            "success": False,
            "code": code,
            "message": message,
            "data": data or {},
            "errors": errors or []
        }, status=status_code)

    @staticmethod
    def paginate_queryset(
        queryset,
        request,
        serializer_class,
        message="عملیات موفقیت‌آمیز بود.",
        status_code=status.HTTP_200_OK,
        code=1000,
        warnings=None,
        extra_data=None,
        data_key='items'
    ):
        """
        پاسخ صفحه‌بندی‌شده برای لیست‌ها.

        Args:
            queryset (QuerySet): مجموعه داده‌ها
            request (Request): درخواست DRF
            serializer_class (Serializer): کلاس سریالایزر
            message (str): پیام موفقیت
            status_code (int): کد HTTP
            code (int): کد اپلیکیشن
            warnings (list): هشدارها
            extra_data (dict): اطلاعات اضافی
            data_key (str): کلید خروجی لیست

        Returns:
            Response: پاسخ با داده‌های صفحه‌بندی شده
        """
        paginator = DefaultPageNumberPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request) or []
        serializer = serializer_class(paginated_queryset, many=True)

        response_data = {data_key: serializer.data}

        if extra_data:
            response_data["extra_data"] = extra_data

        total_pages = paginator.page.paginator.num_pages
        current_page = paginator.page.number

        meta = {
            "total_count": paginator.page.paginator.count,
            "total_pages": total_pages,
            "current_page": current_page,
            "page_size": paginator.get_page_size(request),
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "timestamp": timezone.now(),
            "is_first_page": current_page == 1,
            "is_last_page": current_page == total_pages,
            "items_on_page": len(response_data[data_key]),
            "has_more": paginator.page.has_next(),
        }

        return BaseResponse.success(
            message=message,
            data=response_data,
            status_code=status_code,
            code=code,
            warnings=warnings,
            meta=meta
        )
