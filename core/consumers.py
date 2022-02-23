import json
from channels.generic.websocket import JsonWebsocketConsumer


class GameConsumer(JsonWebsocketConsumer):
    async def connect(self):
        pass

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass

    async def send_message(self, res):
        pass
