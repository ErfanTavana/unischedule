from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from unischedule.core.base_response import BaseResponse
from unischedule.core.error_codes import ErrorCodes
from unischedule.core.exceptions import CustomValidationError
from unischedule.core.success_codes import SuccessCodes

from institutions.services import institution_service


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_institutions_view(request):
    """GET - Fetch all institutions visible to the authenticated user.

    Flow:
        1. Resolve ``request.user`` so we can audit who triggered the read operation.
        2. Delegate to :mod:`institutions.services.institution_service` to assemble the
           serialized list of institutions.
        3. Wrap the payload with :class:`BaseResponse` for consistent API responses.
    """

    request.user  # Access for clarity; no additional filtering required yet.
    institutions = institution_service.list_institutions()
    return BaseResponse.success(
        message=SuccessCodes.INSTITUTION_LISTED["message"],
        code=SuccessCodes.INSTITUTION_LISTED["code"],
        data={"institutions": institutions},
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_institution_view(request):
    """POST - Create a new institution scoped by the authenticated staff user.

    Flow:
        1. Access ``request.user`` to ensure the caller is authenticated.
        2. Pass the raw payload to the service so validations (including slug uniqueness)
           execute in a single place.
        3. Return the normalized institution data via the shared response helper.
    """

    request.user  # Used for auditing/logging in middleware; no direct usage yet.
    try:
        institution = institution_service.create_institution(request.data)
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail.get("errors", []),
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
            message=ErrorCodes.INSTITUTION_CREATION_FAILED["message"],
            code=ErrorCodes.INSTITUTION_CREATION_FAILED["code"],
            status_code=ErrorCodes.INSTITUTION_CREATION_FAILED["status_code"],
            errors=ErrorCodes.INSTITUTION_CREATION_FAILED["errors"],
        )

    return BaseResponse.success(
        message=SuccessCodes.INSTITUTION_CREATED["message"],
        code=SuccessCodes.INSTITUTION_CREATED["code"],
        data={"institution": institution},
        status_code=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_institution_view(request, institution_id: int):
    """GET - Retrieve a single institution after ensuring the caller is authenticated.

    Flow:
        1. Access the requesting user to assert authentication.
        2. Ask the service layer for the institution; it raises if the ID is invalid.
        3. Surface the resulting DTO inside a success response object.
    """

    request.user  # Authentication already enforced by DRF permissions.
    try:
        institution = institution_service.get_institution_by_id_or_404(institution_id)
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail.get("errors", []),
        )
    return BaseResponse.success(
        message=SuccessCodes.INSTITUTION_RETRIEVED["message"],
        code=SuccessCodes.INSTITUTION_RETRIEVED["code"],
        data={"institution": institution},
    )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_institution_view(request, institution_id: int):
    """PUT/PATCH - Update an institution owned by the authenticated tenant.

    Flow:
        1. Grab the authenticated user for audit purposes.
        2. Resolve the institution via the service helper to guarantee existence.
        3. Forward the incoming payload to the service so validation, slug checks,
           and persistence stay centralized.
    """

    request.user
    try:
        institution_obj = institution_service.get_institution_instance_or_404(institution_id)
        updated = institution_service.update_institution(institution_obj, request.data)
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail.get("errors", []),
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
            message=ErrorCodes.INSTITUTION_UPDATE_FAILED["message"],
            code=ErrorCodes.INSTITUTION_UPDATE_FAILED["code"],
            status_code=ErrorCodes.INSTITUTION_UPDATE_FAILED["status_code"],
            errors=ErrorCodes.INSTITUTION_UPDATE_FAILED["errors"],
        )

    return BaseResponse.success(
        message=SuccessCodes.INSTITUTION_UPDATED["message"],
        code=SuccessCodes.INSTITUTION_UPDATED["code"],
        data={"institution": updated},
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_institution_view(request, institution_id: int):
    """DELETE - Soft delete an institution after authentication checks.

    Flow:
        1. Fetch the user to ensure permissions are evaluated.
        2. Ask the service for the institution instance; it raises on missing ID.
        3. Delegate the deletion to the service so auditing and soft delete logic are shared.
    """

    request.user
    try:
        institution_obj = institution_service.get_institution_instance_or_404(institution_id)
        institution_service.delete_institution(institution_obj)
    except CustomValidationError as exc:
        return BaseResponse.error(
            message=exc.detail["message"],
            code=exc.detail["code"],
            status_code=exc.status_code,
            errors=exc.detail.get("errors", []),
        )
    except Exception:
        return BaseResponse.error(
            message=ErrorCodes.INSTITUTION_DELETION_FAILED["message"],
            code=ErrorCodes.INSTITUTION_DELETION_FAILED["code"],
            status_code=ErrorCodes.INSTITUTION_DELETION_FAILED["status_code"],
            errors=ErrorCodes.INSTITUTION_DELETION_FAILED["errors"],
        )

    return BaseResponse.success(
        message=SuccessCodes.INSTITUTION_DELETED["message"],
        code=SuccessCodes.INSTITUTION_DELETED["code"],
    )
