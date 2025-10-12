from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework.authtoken.models import Token

User = get_user_model()


def get_token_by_user(user: User) -> Token | None:
    """Retrieve the first authentication token associated with ``user``."""

    return Token.objects.filter(user=user).first()


def get_or_create_token_by_user(user: User) -> Token:
    """Return an authentication token for ``user``, creating it when needed."""

    token = get_token_by_user(user)
    if token is not None:
        return token

    try:
        return Token.objects.create(user=user)
    except IntegrityError:
        # Another request may have created the token concurrently; fetch it now.
        return Token.objects.get(user=user)


def delete_token(token: Token) -> None:
    """
    Delete the given token.
    """
    token.delete()
