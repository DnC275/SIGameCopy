import json

import channels.sessions
from channels.generic.websocket import JsonWebsocketConsumer


class GameConsumer(JsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = 'room_%s' % self.room_name

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def send_message(self, res):
        pass
