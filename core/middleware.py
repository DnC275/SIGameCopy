import time

from django.conf import settings
from django.utils.functional import LazyObject
from channels.db import database_sync_to_async
from channels.sessions import CookieMiddleware

from .models import Player

try:
    from django.utils.http import http_date
except ImportError:
    from django.utils.http import cookie_date as http_date


class InstanceCookieJWTAuthWrapper:
    save_message_types = ["http.response.start"]

    cookie_response_message_types = ["http.response.start"]

    def __init__(self, scope, send):
        self.cookie_name = settings.TOKEN_COOKIE_NAME
        # self.session_store = import_module(settings.SESSION_ENGINE).SessionStore

        self.scope = dict(scope)

        if "player" in self.scope:
            # There's already session middleware of some kind above us, pass
            # that through
            self.activated = False
        else:
            # Make sure there are cookies in the scope
            if "cookies" not in self.scope:
                raise ValueError(
                    "No cookies in scope - CookieJWTMiddleware needs to run "
                    "inside of CookieMiddleware."
                )
            # Parse the headers in the scope into cookies
            self.scope["player"] = LazyObject()
            self.activated = True

        # Override send
        self.real_send = send

    async def resolve_player(self):
        token = self.scope["cookies"].get(self.cookie_name)
        self.scope["player"]._wrapped = await database_sync_to_async(
            Player.get_by_jwt
        )(token)

    async def send(self, message):
        """
        Overridden send that also does session saves/cookies.
        """
        # Only save session if we're the outermost session middleware
        if self.activated:
            # modified = self.scope["player"].modified
            empty = self.scope["player"] is None
            # If this is a message type that we want to save on, and there's
            # changed data, save it. We also save if it's empty as we might
            # not be able to send a cookie-delete along with this message.
            if (
                message["type"] in self.save_message_types
                and message.get("status", 200) != 500
                # and (modified or settings.SESSION_SAVE_EVERY_REQUEST)
            ):
                # await database_sync_to_async(self.save_session)()
                # If this is a message type that can transport cookies back to the
                # client, then do so.
                if message["type"] in self.cookie_response_message_types:
                    if empty:
                        # Delete cookie if it's set
                        if settings.TOKEN_COOKIE_NAME in self.scope["cookies"]:
                            CookieMiddleware.delete_cookie(
                                message,
                                settings.TOKEN_COOKIE_NAME
                                # path=settings.SESSION_COOKIE_PATH,
                                # domain=settings.SESSION_COOKIE_DOMAIN,
                            )
                    else:
                        # Get the expiry data
                        if self.scope["player"].get_expire_at_browser_close():
                            max_age = None
                            expires = None
                        else:
                            max_age = self.scope["player"].get_expiry_age()
                            expires_time = time.time() + max_age
                            expires = http_date(expires_time)
                        # Set the cookie
                        CookieMiddleware.set_cookie(
                            message,
                            self.cookie_name,
                            self.scope["token"].token,
                            max_age=max_age,
                            expires=expires,
                            # domain=settings.SESSION_COOKIE_DOMAIN,
                            # path=settings.SESSION_COOKIE_PATH,
                            # secure=settings.SESSION_COOKIE_SECURE or None,
                            # httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                            # samesite=settings.SESSION_COOKIE_SAMESITE,
                        )
        # Pass up the send
        return await self.real_send(message)


class CookieJWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        """
        Instantiate a session wrapper for this scope, resolve the session and
        call the inner application.
        """
        wrapper = InstanceCookieJWTAuthWrapper(scope, send)

        await wrapper.resolve_player()

        return await self.inner(wrapper.scope, receive, wrapper.send)


def CookieJWTAuthMiddlewareStack(inner):
    return CookieMiddleware(CookieJWTAuthMiddleware(inner))

