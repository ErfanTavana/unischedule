"""Service layer utilities that expose account profile features."""

from institutions.services import (
    get_institution_logo,
    update_institution_logo,
    delete_institution_logo,
)


def get_authenticated_institution_logo(user, *, context: dict | None = None) -> dict:
    """Return the logo payload for the authenticated user's institution."""

    institution = getattr(user, "institution", None)
    return get_institution_logo(institution, context=context)


def update_authenticated_institution_logo(
    user,
    data: dict,
    *,
    context: dict | None = None,
) -> dict:
    """Update the authenticated user's institution logo."""

    institution = getattr(user, "institution", None)
    return update_institution_logo(institution, data, context=context)


def delete_authenticated_institution_logo(user, *, context: dict | None = None) -> dict:
    """Remove the institution logo associated with the authenticated user."""

    institution = getattr(user, "institution", None)
    return delete_institution_logo(institution, context=context)
