from aiogram import BaseMiddleware
from aiogram.types import Message
from datetime import datetime, timezone
from typing import Callable, Dict, Any, Awaitable, List

from database.database import get_pool


class ActivityTrackerMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ):
        # Проверяем, является ли событие сообщением
        if isinstance(event, Message):
            try:
                pool = await get_pool()
                async with pool.acquire() as conn:
                    await conn.execute(
                        """
                        UPDATE users  
                        SET last_active = $2
                        WHERE user_id = $1
                        """,
                        event.from_user.id, datetime.now(timezone.utc)
                    )
            except Exception as e:
                print(f"Error updating user activity: {e}")

        # Передаем управление следующему обработчику
        return await handler(event, data)