"""
WebSocket Consumers for Real-time Features
المستهلكون WebSocket للميزات الفورية
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from .models import Notification
import logging

logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    """Real-time notifications consumer"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Create user-specific group
        self.group_name = f"notifications_{self.user.id}"
        
        # Join notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.username} connected to notifications")
        
        # Send any pending notifications
        await self.send_pending_notifications()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        logger.info(f"User disconnected from notifications: {close_code}")
    
    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', '')
            
            if message_type == 'mark_as_read':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_read(notification_id)
            elif message_type == 'get_notifications':
                await self.send_pending_notifications()
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in notification consumer")
        except Exception as e:
            logger.error(f"Error in notification consumer: {str(e)}")
    
    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }, cls=DjangoJSONEncoder))
    
    @database_sync_to_async
    def get_pending_notifications(self):
        """Get pending notifications for user"""
        return list(
            Notification.objects.filter(
                recipient=self.user,
                read_at__isnull=True
            ).order_by('-created_at')[:10].values(
                'id', 'title', 'message', 'notification_type', 
                'priority', 'created_at', 'action_url', 'action_text'
            )
        )
    
    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    async def send_pending_notifications(self):
        """Send all pending notifications to client"""
        notifications = await self.get_pending_notifications()
        
        await self.send(text_data=json.dumps({
            'type': 'notifications_list',
            'notifications': notifications,
            'count': len(notifications)
        }, cls=DjangoJSONEncoder))

class ChatConsumer(AsyncWebsocketConsumer):
    """Chat consumer for real-time messaging"""
    
    async def connect(self):
        """Handle chat connection"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send user joined message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': self.user.username,
                'message': f'{self.user.get_full_name() or self.user.username} انضم إلى المحادثة'
            }
        )
    
    async def disconnect(self, close_code):
        """Handle chat disconnection"""
        # Send user left message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': self.user.username,
                'message': f'{self.user.get_full_name() or self.user.username} غادر المحادثة'
            }
        )
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receive message from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': self.user.username,
                    'user_full_name': self.user.get_full_name() or self.user.username,
                    'timestamp': json.dumps(
                        timezone.now(), 
                        cls=DjangoJSONEncoder
                    )
                }
            )
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON received in chat consumer")
        except KeyError:
            logger.error("Missing message key in chat consumer")
    
    async def chat_message(self, event):
        """Send message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'user': event['user'],
            'user_full_name': event['user_full_name'],
            'timestamp': event['timestamp']
        }))
    
    async def user_joined(self, event):
        """Send user joined message"""
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
            'message': event['message']
        }))
    
    async def user_left(self, event):
        """Send user left message"""
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user'],
            'message': event['message']
        }))

class LiveUpdatesConsumer(AsyncWebsocketConsumer):
    """Consumer for live system updates"""
    
    async def connect(self):
        """Handle live updates connection"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Join live updates group
        self.group_name = "live_updates"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"User {self.user.username} connected to live updates")
    
    async def disconnect(self, close_code):
        """Handle live updates disconnection"""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle messages from client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', '')
            
            if message_type == 'subscribe':
                # Subscribe to specific updates
                channels = data.get('channels', [])
                for channel in channels:
                    await self.channel_layer.group_add(
                        f"live_updates_{channel}",
                        self.channel_name
                    )
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in live updates consumer")
    
    async def live_update(self, event):
        """Send live update to client"""
        await self.send(text_data=json.dumps({
            'type': 'live_update',
            'channel': event.get('channel', ''),
            'data': event.get('data', {}),
            'timestamp': json.dumps(
                timezone.now(), 
                cls=DjangoJSONEncoder
            )
        }))

class SystemStatusConsumer(AsyncWebsocketConsumer):
    """Consumer for system status monitoring"""
    
    async def connect(self):
        """Handle system status connection"""
        self.user = self.scope["user"]
        
        # Only allow admin users
        if self.user.is_anonymous or not (self.user.is_staff or self.user.is_superuser):
            await self.close()
            return
        
        self.group_name = "system_status"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f"Admin user {self.user.username} connected to system status")
        
        # Send current system status
        await self.send_system_status()
    
    async def disconnect(self, close_code):
        """Handle system status disconnection"""
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def system_status_update(self, event):
        """Send system status update"""
        await self.send(text_data=json.dumps({
            'type': 'system_status',
            'status': event['status'],
            'metrics': event.get('metrics', {}),
            'timestamp': event.get('timestamp')
        }, cls=DjangoJSONEncoder))
    
    @database_sync_to_async
    def get_system_metrics(self):
        """Get current system metrics"""
        from django.contrib.auth.models import User
        from academic.models import Enrollment
        from courses.models import Course
        
        return {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_courses': Course.objects.count(),
            'active_enrollments': Enrollment.objects.filter(is_active=True).count(),
        }
    
    async def send_system_status(self):
        """Send current system status"""
        metrics = await self.get_system_metrics()
        
        await self.send(text_data=json.dumps({
            'type': 'system_status',
            'status': 'healthy',
            'metrics': metrics,
            'timestamp': json.dumps(
                timezone.now(), 
                cls=DjangoJSONEncoder
            )
        }, cls=DjangoJSONEncoder))

# Utility functions for sending messages to consumers
async def send_notification_to_user(user_id, notification_data):
    """Send notification to specific user"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    group_name = f"notifications_{user_id}"
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )

async def send_live_update(channel, data):
    """Send live update to all subscribers"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    group_name = f"live_updates_{channel}"
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'live_update',
            'channel': channel,
            'data': data
        }
    )

async def send_system_status_update(status, metrics=None):
    """Send system status update to admin users"""
    from channels.layers import get_channel_layer
    from django.utils import timezone
    
    channel_layer = get_channel_layer()
    
    await channel_layer.group_send(
        "system_status",
        {
            'type': 'system_status_update',
            'status': status,
            'metrics': metrics or {},
            'timestamp': json.dumps(
                timezone.now(), 
                cls=DjangoJSONEncoder
            )
        }
    )