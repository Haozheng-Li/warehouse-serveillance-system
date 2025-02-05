import json
import base64
from django.conf import settings
from asgiref.sync import async_to_sync
from django.utils import timezone
from django.shortcuts import reverse
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from django.db.models import ObjectDoesNotExist

from apps.devices.models import Devices, Performance
from apps.record.models import EventLog
from apps.accounts.models import UserSettings
from apps.accounts.send_email import send_detection_warning_email
from .notification_consumer import _async_send_notification, send_notification


def send_device_message(device_id, message, message_type="operation"):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('device{}'.format(device_id), {"type": "group_message",
                                                                            "message": message,
                                                                            "message_type": message_type})


class DeviceConsumer(AsyncWebsocketConsumer):
    group_name = ''
    api_key = ''
    device = None
    device_enable = False
    user = None
    user_id = 0
    user_email = ''

    async def connect(self):
        self.api_key = self.scope["url_route"]["kwargs"].get('api_key', '')
        self.device = await self.get_device()
        if self.device and self.device.is_enable:
            await self.accept()
            await self.on_device_connect()
        else:
            await self.close(code=3003)

    @database_sync_to_async
    def get_device(self):
        try:
            device = Devices.objects.get(api_key=self.api_key)
            if device:
                self.device = device
                self.user = device.user
                self.user_id = device.user.id
                self.user_email = device.user.email
                self.device_enable = device.is_enable
                return device
        except ObjectDoesNotExist:
            return

    async def disconnect(self, close_code):
        await self.update_device_status(active=False)
        if self.device:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            message = "Device: {} is offline.".format(self.device.name)
            await _async_send_notification(self.user_id, message=message, duration=8000, level="warning")

    async def receive(self, text_data=None, bytes_data=None):
        parsed_data = json.loads(text_data)
        message_type = parsed_data.get('message_type')
        message = parsed_data.get('message')

        self.get_device()   # get newest device info

        if not (message_type and message and self.device_enable):
            await self.disconnect(close_code=3003)
            await self.close(code=3003)

        # parse
        if message_type == 'profiler':
            await self.on_profiler_message(message)
        elif message_type == 'detect_event':
            await self.on_detect_event_message(message)
        elif message_type == 'operation_feedback':
            await self.on_operation_feedback_message(message)

    async def group_message(self, event):
        print("send device message {}".format(event))
        message_type = event.get('message_type', 'operation')
        data = {"message": event['message'],
                "message_type": message_type}
        await self.send(text_data=json.dumps(data))

    @database_sync_to_async
    def update_device_status(self, active=True):
        if self.device:
            self.device.last_online = timezone.now()
            self.device.is_activated = True
            self.device.is_active = active
            if active:
                self.device.conversation_num += 1
            self.device.save()

    @database_sync_to_async
    def on_profiler_message(self, performance_dict):
        if self.device:
            performance = Performance()
            performance.device = self.device
            performance.cpu_rate = performance_dict['cpu_used_rate']
            performance.mem_rate = performance_dict['mem_used_rate']
            performance.disk_write_io = performance_dict['disk_io_read']
            performance.disk_read_io = performance_dict['disk_io_write']
            performance.save()

    async def on_device_connect(self):
        if self.device:
            await self.update_device_status(active=True)
            self.group_name = 'device{}'.format(self.device.id)
            await self.channel_layer.group_add(self.group_name, self.channel_name)

            message = "Device: {} is online.".format(self.device.name)
            await _async_send_notification(self.user_id, message=message, duration=8000,
                                    jump_url=reverse('device_detail', kwargs={'device_id': self.device.id}))

            if self.device.enable_profiler:
                init_message = {"message": {'operation': 'enable', 'operation_type': 'profiler'},
                                "message_type": 'init'}
                await self.send(json.dumps(init_message))
            if self.device.enable_intruder_detection:
                init_message = {"message": {'operation': 'enable', 'operation_type': 'intruder_detection'},
                                "message_type": 'init'}
                await self.send(json.dumps(init_message))

    @database_sync_to_async
    def on_detect_event_message(self, event_data):
        data_type = event_data.get('data_type', '')
        file_data = event_data.get('data_file', '')
        intruder_event_type = event_data.get('intruder_type', 0)
        data_file_name = event_data.get('data_file_name', 0)
        if self.device and data_type and file_data and intruder_event_type:
            file_data = base64.b64decode(file_data)
            media_path = 'record/detection_event/' + data_file_name
            with open(settings.MEDIA_ROOT / media_path, "wb") as f:
                f.write(file_data)

            event_record = EventLog()
            event_record.device = self.device
            event_record.user = self.user
            event_record.event = intruder_event_type
            event_record.message = 'Intruder event {}'.format(intruder_event_type)
            event_record.action = 'enter mode'.format(intruder_event_type)
            event_record.resource_type = 'video' if intruder_event_type == 4 else 'image'
            event_record.resource_url = str(media_path)
            event_record.save()
            send_detection_warning_email(self.user_id, self.user_email, intruder_event_type, "127.0.0.1:8000/media/{}".format(media_path))

            send_notification(self.user_id, message="Detect Intruder Event {}".format(intruder_event_type), duration=8000,
                              level="error", refresh=False, notification_type='swal', title='Intruder Event',
                              footer='<a href="{}">Click here to check event detail</a>'.format(reverse('device_detail',
                                                                                                        kwargs={'device_id': self.device.id})))

    @database_sync_to_async
    def on_operation_feedback_message(self, message):
        operation = message.get('operation', '')
        operation_type = message.get('operation_type', '')

        operation_feedback_message = 'Device {} {} {}'.format(self.device.name, operation, operation_type)
        level = 'success' if operation == 'enable' else 'danger'
        if self.device:
            if operation_type == 'profiler':
                self.device.enable_profiler = operation == 'enable'
                self.device.save()
                send_notification(self.user_id, message=operation_feedback_message, duration=3000,
                                  level=level, refresh=True)
            elif operation_type == 'intruder_detection':
                self.device.enable_intruder_detection = operation == 'enable'
                self.device.save()
                send_notification(self.user_id, message=operation_feedback_message, duration=3000,
                                  level=level, refresh=True)
            elif operation_type == 'restart':
                send_notification(self.user_id, message=operation_feedback_message, duration=8000,
                                  level=level, refresh=False)

    @database_sync_to_async
    def check_notification_availability(self, user_obj):
        try:
            user_settings = UserSettings.objects.get(user=user_obj)
            if user_settings:
                return user_settings.web_notification
        except ObjectDoesNotExist:
            pass
        return False
