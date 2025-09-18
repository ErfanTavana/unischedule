from __future__ import annotations

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from unischedule.core.base_response import BaseResponse
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes

from displays.services import display_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_display_screens_view(request):
    institution = request.user.institution
    try:
        screens = display_service.list_display_screens(institution)
        return BaseResponse.success(
            message=SuccessCodes.DISPLAY_SCREEN_LISTED["message"],
            code=SuccessCodes.DISPLAY_SCREEN_LISTED["code"],
            data={"screens": screens},
        )
    except CustomValidationError as exc:
        return JsonResponse(
            {
                "success": False,
                "code": exc.detail["code"],
                "message": exc.detail["message"],
                "data": exc.detail.get("data", {}),
                "errors": exc.detail.get("errors", []),
            },
            status=exc.status_code,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_display_screen_view(request):
    institution = request.user.institution
    try:
        screen = display_service.create_display_screen(request.data, institution)
        return BaseResponse.success(
            message=SuccessCodes.DISPLAY_SCREEN_CREATED["message"],
            code=SuccessCodes.DISPLAY_SCREEN_CREATED["code"],
            data={"screen": screen},
            status_code=status.HTTP_201_CREATED,
        )
    except CustomValidationError as exc:
        return JsonResponse(
            {
                "success": False,
                "code": exc.detail["code"],
                "message": exc.detail["message"],
                "data": exc.detail.get("data", {}),
                "errors": exc.detail.get("errors", []),
            },
            status=exc.status_code,
        )
    except ValidationError as exc:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=exc.detail,
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.DISPLAY_SCREEN_CREATION_FAILED["message"],
            code=ErrorCodes.DISPLAY_SCREEN_CREATION_FAILED["code"],
            status_code=ErrorCodes.DISPLAY_SCREEN_CREATION_FAILED["status_code"],
            errors=ErrorCodes.DISPLAY_SCREEN_CREATION_FAILED["errors"],
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_display_screen_view(request, screen_id: int):
    institution = request.user.institution
    try:
        screen = display_service.get_display_screen_by_id_or_404(screen_id, institution)
        return BaseResponse.success(
            message=SuccessCodes.DISPLAY_SCREEN_RETRIEVED["message"],
            code=SuccessCodes.DISPLAY_SCREEN_RETRIEVED["code"],
            data={"screen": screen},
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_display_screen_view(request, screen_id: int):
    institution = request.user.institution
    try:
        screen_instance = display_service.get_display_screen_instance_or_404(screen_id, institution)
        updated = display_service.update_display_screen(screen_instance, request.data)
        return BaseResponse.success(
            message=SuccessCodes.DISPLAY_SCREEN_UPDATED["message"],
            code=SuccessCodes.DISPLAY_SCREEN_UPDATED["code"],
            data={"screen": updated},
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )
    except ValidationError as exc:
        return BaseResponse.error(
            message=ErrorCodes.VALIDATION_FAILED["message"],
            code=ErrorCodes.VALIDATION_FAILED["code"],
            status_code=ErrorCodes.VALIDATION_FAILED["status_code"],
            errors=exc.detail,
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.DISPLAY_SCREEN_UPDATE_FAILED["message"],
            code=ErrorCodes.DISPLAY_SCREEN_UPDATE_FAILED["code"],
            status_code=ErrorCodes.DISPLAY_SCREEN_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.DISPLAY_SCREEN_UPDATE_FAILED["errors"],
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_display_screen_view(request, screen_id: int):
    institution = request.user.institution
    try:
        screen_instance = display_service.get_display_screen_instance_or_404(screen_id, institution)
        display_service.delete_display_screen(screen_instance)
        return BaseResponse.success(
            message=SuccessCodes.DISPLAY_SCREEN_DELETED["message"],
            code=SuccessCodes.DISPLAY_SCREEN_DELETED["code"],
        )
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.DISPLAY_SCREEN_DELETION_FAILED["message"],
            code=ErrorCodes.DISPLAY_SCREEN_DELETION_FAILED["code"],
            status_code=ErrorCodes.DISPLAY_SCREEN_DELETION_FAILED["status_code"],
            errors=ErrorCodes.DISPLAY_SCREEN_DELETION_FAILED["errors"],
        )


@require_GET
def public_display_view(request, slug: str):
    wants_html = request.GET.get("format") == "html" or "text/html" in request.META.get("HTTP_ACCEPT", "")
    try:
        screen = display_service.get_display_screen_by_slug_or_404(slug)
        payload = display_service.build_public_payload(screen)
    except CustomValidationError as exc:
        if wants_html:
            return render(
                request,
                "displays/public.html",
                {
                    "error": exc.detail["message"],
                    "screen": None,
                    "sessions": [],
                    "filters": [],
                    "messages": [],
                    "generated_at": None,
                    "refresh_interval": 60,
                },
                status=exc.status_code,
            )
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail["errors"],
            data=exc.detail.get("data"),
        )

    if wants_html:
        screen_data = payload["screen"]
        context = {
            "screen": screen_data,
            "sessions": payload["sessions"],
            "filters": payload["filters"],
            "messages": payload["messages"],
            "generated_at": payload["generated_at"],
            "refresh_interval": screen_data.get("refresh_interval", 60),
        }
        return render(request, "displays/public.html", context)

    return JsonResponse(
        {
            "success": True,
            "code": SuccessCodes.DISPLAY_SCREEN_RENDERED["code"],
            "message": SuccessCodes.DISPLAY_SCREEN_RENDERED["message"],
            "data": payload,
            "warnings": [],
            "meta": {},
        }
    )
