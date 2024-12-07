from asgiref.sync import sync_to_async
from rtc_app.utils import UserAuthService
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import * 
import logging

# Asynchronous wrapper to fetch user profile
async def get_user_details(auth_token):
    """
    Asynchronous wrapper to call the user management API for user details.
    """
    return await sync_to_async(UserAuthService.get_user_profile)(auth_token)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger = logging.getLogger(__name__)
        logger.debug("WebSocket connect: %s", self.scope)
        
        # Extract the auth_token from the WebSocket query parameters
        self.auth_token = self.scope.get('query_string', '').decode().split('=')[1]
        
        # Fetch user details from the user authentication API
        user_details = await get_user_details(self.auth_token)
        
        # Authentication check
        if "error" in user_details:
            print("Authentication failed", user_details)
            await self.close(code=4001)  # Close connection with a specific code
            return

        self.user_id = user_details.get('id', None)  # Fetch the user_id from the profile API
        if not self.user_id:
            await self.close(code=4002)
            return

        self.recipient_id = self.scope['url_route']['kwargs'].get('recipient_id')  # Recipient user_id is passed via WebSocket URL
        if not self.recipient_id:
            await self.close(code=4003)
            return

        # Join the WebSocket connection using both user IDs (sender and recipient)
        self.channel_name = f"{self.user_id}_{self.recipient_id}"

        # Accept the websocket connection
        await self.accept()
        
        # Send a welcome message or notify that the connection is established
        await self.send(text_data=json.dumps({
            'message': f'Connected to {self.recipient_id}!',
        }))

    async def disconnect(self, close_code):
        # Handle disconnection
        await self.send(text_data=json.dumps({
            'message': f'Disconnected from {self.recipient_id}',
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json.get('message')

        if message_content:
            # Save the message to the database
            await self.save_message(self.user_id, self.recipient_id, message_content)

            # Send the message to the WebSocket
            recipient_channel_name = f"{self.recipient_id}_{self.user_id}"
            
            await self.channel_layer.group_send(
                recipient_channel_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender_id': self.user_id,
                    'recipient_id': self.recipient_id,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender_id = event['sender_id']
        recipient_id = event['recipient_id']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_id': sender_id,
            'recipient_id': recipient_id,
        }))

    @sync_to_async
    def save_message(self, sender_id, recipient_id, content):
        """
        Save the chat message to the database with sender and recipient IDs.
        """
        message = Message(sender=sender_id, recipient=recipient_id, content=content)
        message.save()

    @sync_to_async
    def get_all_messages(self, sender_id, recipient_id):
        """
        Retrieve all messages exchanged between two users (sender and recipient).
        """
        return Message.objects.filter(
            sender=sender_id, recipient=recipient_id
        ).order_by('timestamp')