import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ParkingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "parking_updates"

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from room group
    async def slot_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'slot_update',
            'slot_id': event['slot_id'],
            'is_available': event['is_available'],
            'location_id': event['location_id']
        }))
