"""
Django Channels WebSocket consumer'ları.

/ws/farms/{farm_id}/live/   — çiftlik canlı sensör + komut durumu
/ws/notifications/          — kullanıcı bildirim akışı
"""

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class FarmLiveConsumer(AsyncJsonWebsocketConsumer):
    """
    Çiftliğe ait canlı sensör okumalarını ve komut durumu güncellemelerini iletir.
    Bağlantı kurulmadan önce çiftlik üyeliği kontrol edilir.
    """

    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return

        farm_id = self.scope["url_route"]["kwargs"]["farm_id"]
        if not await self._is_member(user, farm_id):
            await self.close(code=4403)
            return

        self.group_name = f"farm-{farm_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        # İstemciden gelen mesajlar yok sayılır — bu kanal salt okunurdur
        pass

    # --- Kanal katmanı mesaj işleyicileri ---

    async def sensor_reading(self, event):
        await self.send_json({"type": "sensor_reading", "data": event["data"]})

    async def command_status(self, event):
        await self.send_json({"type": "command_status", "data": event["data"]})

    @database_sync_to_async
    def _is_member(self, user, farm_id) -> bool:
        from apps.accounts.models import FarmMembership

        return FarmMembership.objects.filter(user=user, farm_id=farm_id).exists()


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """
    Kullanıcıya özgü bildirim akışı.
    Her kullanıcı kendi grubuna (user-{id}) katılır.
    """

    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return

        self.group_name = f"user-{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        pass

    async def notification(self, event):
        await self.send_json({"type": "notification", "data": event["data"]})
