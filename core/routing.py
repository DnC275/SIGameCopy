# from django.conf.urls import url
from django.urls import re_path

from core.rooms.consumers import GameConsumer, RoomsListConsumer


websocket_urlpatterns = [
    re_path(r'^ws/rooms/(?P<room_id>\w+)/$', GameConsumer.as_asgi()),
    re_path(r'^ws/rooms/', RoomsListConsumer.as_asgi()),
]
