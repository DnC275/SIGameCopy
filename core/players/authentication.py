import jwt
from django.conf import settings
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from core.players.models import Player


class JWTAuthentication(TokenAuthentication):

    def authenticate(self, request):
        # Check if 'auth_token' is in the request cookies.
        # Give precedence to 'Authorization' header.
        player = None
        token = request.headers.get('Authorization')
        if token:
            player = Player.get_by_jwt(token)
            #
            # if player is None:
            #     raise exceptions.AuthenticationFailed('Invalid token')

        return player, token

