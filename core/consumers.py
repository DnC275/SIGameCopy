import json

import channels.sessions
from channels.generic.websocket import JsonWebsocketConsumer
from channels.auth import CookieMiddleware


class GameConsumer(JsonWebsocketConsumer):
    def connect(self):
        print(self.scope['user'])
        self.close()

        # self.room_name = self.scope['url_route']['kwargs']['room_code']
        # self.room_group_name = 'room_%s' % self.room_name

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        pass

    def send_message(self, res):
        pass


class RoomsListConsumer(JsonWebsocketConsumer):
    def connect(self):
        print(self.scope['user'])

        self.connection_id = self.scope['user'].id
        # self.room_group_name = 'room_%s' % self.room_name

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        pass

    def send_message(self, res):
        pass