"""Account-facing endpoints for managing institution profile assets."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from accounts.services import (
    get_authenticated_institution_logo,
    update_authenticated_institution_logo,
    delete_authenticated_institution_logo,
)
from unischedule.core.base_response import BaseResponse
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def institution_logo_view(request):
    """Expose CRUD-style operations for the institution logo of the current user."""

    context = {"request": request}

    try:
        if request.method == "GET":
            payload = get_authenticated_institution_logo(request.user, context=context)
            return BaseResponse.success(
                message=SuccessCodes.INSTITUTION_LOGO_RETRIEVED["message"],
                code=SuccessCodes.INSTITUTION_LOGO_RETRIEVED["code"],
                data={"institution": payload},
                status_code=status.HTTP_200_OK,
            )

        if request.method == "PUT":
            payload = update_authenticated_institution_logo(
                request.user,
                request.data,
                context=context,
            )
            return BaseResponse.success(
                message=SuccessCodes.INSTITUTION_LOGO_UPDATED["message"],
                code=SuccessCodes.INSTITUTION_LOGO_UPDATED["code"],
                data={"institution": payload},
                status_code=status.HTTP_200_OK,
            )

        payload = delete_authenticated_institution_logo(request.user, context=context)
        return BaseResponse.success(
            message=SuccessCodes.INSTITUTION_LOGO_DELETED["message"],
            code=SuccessCodes.INSTITUTION_LOGO_DELETED["code"],
            data={"institution": payload},
            status_code=status.HTTP_200_OK,
        )

    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail.get("errors", []),
            data=exc.detail.get("data", {}),
        )
    except Exception:
        failure_mapping = {
            "GET": ErrorCodes.INSTITUTION_LOGO_RETRIEVE_FAILED,
            "PUT": ErrorCodes.INSTITUTION_LOGO_UPDATE_FAILED,
            "DELETE": ErrorCodes.INSTITUTION_LOGO_DELETE_FAILED,
        }
        failure = failure_mapping[request.method]
        return BaseResponse.error(
            message=failure["message"],
            code=failure["code"],
            status_code=failure["status_code"],
            errors=failure["errors"],
            data=failure.get("data", {}),
        )
