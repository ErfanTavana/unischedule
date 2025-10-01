"""Utility helpers that standardise API responses across the project.

``BaseResponse`` wraps common success/error envelopes and paging logic so that
viewsets only need to supply their payloads. Keeping response structure in one
place guarantees a uniform contract for the front-end and simplifies
documentation.
"""

from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone


class DefaultPageNumberPagination(PageNumberPagination):
    """Project-wide pagination defaults used by :func:`BaseResponse.paginate_queryset`.

    The class exposes ``page_size`` through a query parameter so clients can
    request small or large pages without having to override pagination per view.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class BaseResponse:
    """Helper for building consistent DRF ``Response`` objects.

    Developers can call :meth:`success`, :meth:`error`, or
    :meth:`paginate_queryset` from viewsets or services to avoid repeating the
    envelope shape each time an API endpoint returns data.
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
        """Return a successful API response using the shared payload contract.

        Args:
            message (str): Human-friendly success message shown to clients.
            data (dict): Main payload returned to the caller.
            status_code (int): HTTP status code to attach to the response.
            code (int): Internal logical code that front-end apps can branch on.
            warnings (list): Non-blocking warnings worth surfacing to the user.
            meta (dict): Optional metadata (e.g. paging info) bundled alongside
                the main payload.

        Returns:
            Response: A DRF ``Response`` instance following the "success" schema.
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
        """Return an error response with a predictable envelope for clients.

        Args:
            message (str): Primary error message for the user interface.
            errors (list): Detailed validation or domain errors.
            status_code (int): HTTP status code representing the failure.
            code (int): Application-level error code referenced in documentation.
            data (dict): Optional contextual data explaining the failure state.

        Returns:
            Response: A DRF ``Response`` containing the standard error payload.
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
        """Serialize and wrap a queryset in the standard paginated response.

        Args:
            queryset (QuerySet): Data collection that should be paginated.
            request (Request): DRF request used to resolve paging parameters.
            serializer_class (Serializer): Serializer used to render each item.
            message (str): Success message to display to clients.
            status_code (int): HTTP status code for the response.
            code (int): Logical success code that complements HTTP status codes.
            warnings (list): Optional warnings that should accompany the result.
            extra_data (dict): Extra payload that should travel with the list.
            data_key (str): Dict key under which the serialized list is stored.

        Returns:
            Response: DRF response compatible with :class:`DefaultPageNumberPagination`.
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
