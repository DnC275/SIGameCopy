import json
import channels.layers
from datetime import datetime

from asgiref.sync import async_to_sync
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
# from datetime import datetime

from core.rooms.models import *



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
        print('Connecting...')
        # self.channel_name = 'channel_%s' % self.scope['user'].id
        time = datetime.now().time()
        self.connection_name = 'connection_%s' % ('_'.join([str(time.hour), str(time.second), str(time.microsecond)]))

        async_to_sync(self.channel_layer.group_add)(
            'lobby',
            self.channel_name
        )

        self.accept()

        rooms = Room.get_all_room_names()
        # async_to_sync(self.channel_layer.group_send)('lobby', {
        #     'type': 'send_updates',
        #     'message': 'aboba'
        # })

        print('Connected')

        self.send_json({
            'rooms': rooms
        })

    def send_updates(self, event):
        print('Sending updates...')
        self.send_json({
            'rooms': event['message']
        })
        print('Updates sent')

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            'lobby',
            self.channel_name
        )

    def receive(self, text_data):
        pass
