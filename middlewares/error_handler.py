from typing import Callable, Dict, Any
import logging
from aiogram import Bot
from aiogram.types import Message
from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ErrorHandlerMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, admin_ids: list[int]):
        super().__init__()
        self.bot = bot
        self.admin_ids = admin_ids

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Any],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            error_msg = f"TelegramBadRequest: {str(e)}"
            await self._handle_error(event, error_msg, "⚠️ Произошла ошибка при обработке запроса")
        except TelegramAPIError as e:
            error_msg = f"TelegramAPIError: {str(e)}"
            await self._handle_error(event, error_msg, "🚫 Ошибка API Telegram")
        except Exception as e:
            error_msg = f"Unhandled error: {str(e)}"
            await self._handle_error(event, error_msg, "❌ Произошла непредвиденная ошибка")
            await self._notify_admins(error_msg)
        return None

    async def _handle_error(self, event: Message, log_msg: str, user_msg: str):
        logger.error(log_msg, exc_info=True)
        try:
            await event.answer(user_msg)
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}", exc_info=True)

    async def _notify_admins(self, error_msg: str):
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(
                    admin_id,
                    f"🚨 Ошибка в боте:\n{error_msg}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}", exc_info=True)
