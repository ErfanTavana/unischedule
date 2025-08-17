from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

User = get_user_model()


def get_token_by_user(user: User) -> Token | None:
    """
    Retrieve token for a given user.
    """
    return Token.objects.filter(user=user).first()


def delete_token(token: Token) -> None:
    """
    Delete the given token.
    """
    token.delete()
