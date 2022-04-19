import time
import django.db

from django.conf import settings
from django.utils.functional import LazyObject
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from django.utils.deprecation import MiddlewareMixin


from core.players.models import Player

try:
    from django.utils.http import http_date
except ImportError:
    from django.utils.http import cookie_date as http_date


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if settings.TOKEN_HEADER_NAME in headers:
            token_name, token_key = headers[settings.TOKEN_HEADER_NAME].decode().split()

            django.db.close_old_connections()
            scope['user'] = Player.get_by_jwt(token_key)
        return await self.inner(scope, receive, send)


JWTAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))


# class CustomMiddleware(MiddlewareMixin):
#     def __call__(self, request):
#         response = super(CustomMiddleware, self).__call__(request)
#         print(response.headers)
#         return response

    # def process_response(
    #         self, request, response
    # ):
    #     print(response.headers)
    #     return response

