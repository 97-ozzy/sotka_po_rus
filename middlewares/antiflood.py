import time
from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, cooldown_seconds: float = 0.6):  # теперь можно float
        self.cooldown = cooldown_seconds
        self.users_timestamps: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Any],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        now = time.time()

        last_time = self.users_timestamps.get(user_id)
        if last_time and now - last_time < self.cooldown:
            wait_time = round(self.cooldown - (now - last_time), 1)
            await event.answer(f"Пожалуйста подожди 🕒\n"
                               f"Не делай много запросов 🥰")
            return None

        self.users_timestamps[user_id] = now
        return await handler(event, data)
