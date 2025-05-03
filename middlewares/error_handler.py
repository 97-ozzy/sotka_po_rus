from typing import Callable, Dict, Any
import logging
from aiogram import Bot
from aiogram.types import Update, Message, CallbackQuery
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest

from keyboards.inline_kb import menu_button

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _handle_error(event: Any, log_msg: str, user_msg: str):
    logger.error(f"{log_msg}\nEvent: {event}", exc_info=True)
    try:
        # Determine the action that caused the error
        action = "неизвестное действие"
        if isinstance(event, Update):
            if event.message and event.message.text:
                action = f"команда или сообщение: '{event.message.text}'"
            elif event.callback_query and event.callback_query.data:
                action = f"действие с callback: '{event.callback_query.data}'"
        elif isinstance(event, Message) and event.text:
            action = f"команда или сообщение: '{event.text}'"
        elif isinstance(event, CallbackQuery) and event.data:
            action = f"действие с callback: '{event.data}'"

        # Construct user message
        full_user_msg = (
            f"{user_msg}\n\n"
            f"Пожалуйста, сообщите в поддержку @ozzy970 о проблеме.\n"
            f"Укажите, что произошло: {user_msg.lower()}.\n"
            f"Действие, перед которым возникла ошибка: {action}."
        )



        # Send message to user with inline keyboard
        if isinstance(event, Update):
            if event.message:
                await event.message.answer(full_user_msg, reply_markup=menu_button())
            elif event.callback_query:
                await event.callback_query.message.answer(full_user_msg, reply_markup=menu_button())
            else:
                logger.warning("No suitable method to send error message to user")
        elif isinstance(event, Message):
            await event.answer(full_user_msg, reply_markup=menu_button())
        elif isinstance(event, CallbackQuery):
            await event.message.answer(full_user_msg, reply_markup=menu_button())
        else:
            logger.warning(f"Unknown event type: {type(event)}")
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}", exc_info=True)


class ErrorHandlerMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, admin_ids: list[int]):
        super().__init__()
        self.bot = bot
        self.admin_ids = admin_ids

    async def __call__(
            self,
            handler: Callable[[Any, Dict[str, Any]], Any],
            event: Any,  # Allow any event type (Update, Message, CallbackQuery)
            data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)
        except TelegramBadRequest as e:
            error_msg = f"TelegramBadRequest: {str(e)}"
            await _handle_error(event, error_msg, "⚠️ Произошла ошибка при обработке запроса")
        except TelegramAPIError as e:
            error_msg = f"TelegramAPIError: {str(e)}"
            await _handle_error(event, error_msg, "🚫 Ошибка API Telegram")
        except Exception as e:
            error_msg = f"Unhandled error: {str(e)}"
            await _handle_error(event, error_msg, "❌ Произошла непредвиденная ошибка")
            await self._notify_admins(error_msg, event)
        return None

    async def _notify_admins(self, error_msg: str, event: Any):
        event_details = f"Event: {event}"
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(
                    admin_id,
                    f"🚨 Ошибка в боте:\n{error_msg}\n\n{event_details}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}", exc_info=True)