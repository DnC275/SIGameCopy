import jwt
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from .models import Player


class CookieAuthentication(TokenAuthentication):
    """
    Extend the TokenAuthentication class to support cookie based authentication
    """
    def authenticate(self, request):
        # Check if 'auth_token' is in the request cookies.
        # Give precedence to 'Authorization' header.
        player, token = None, None
        if 'access_token' in request.COOKIES:
            token = request.COOKIES['access_token']

            player = Player.get_by_jwt(token)

            if player is None:
                raise exceptions.AuthenticationFailed('Invalid token')

        return player, token

