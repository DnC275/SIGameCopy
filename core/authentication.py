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
        if 'access_token' in request.COOKIES:
            token = request.COOKIES['access_token']
            payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')

            if 'id' not in payload:
                raise exceptions.AuthenticationFailed('Invalid token')

            player = Player.objects.get(id=payload['id'])

            if not player:
                raise exceptions.AuthenticationFailed('Player does not exist')

            return player, token

        return super().authenticate(request)
