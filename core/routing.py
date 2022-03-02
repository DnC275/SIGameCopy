# from django.conf.urls import url
from django.urls import re_path
from .consumers import GameConsumer


websocket_urlpatterns = [
    re_path(r'^ws/game/(?P<room_id>\w+)/$', GameConsumer.as_asgi()),
]
