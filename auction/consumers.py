import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer


ROOM_NAME = 'auction_room'
ROOM_GROUP_NAME = 'group_{}'.format(ROOM_NAME)

class ChannelConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = ROOM_NAME
        self.room_group_name = ROOM_GROUP_NAME

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))


def ws_send(message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        ROOM_GROUP_NAME,
        {
            'type': 'chat_message',
            'message': message
        }
    )
