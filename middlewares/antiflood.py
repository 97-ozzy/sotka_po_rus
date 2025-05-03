import time
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable, List, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Dictionary to store the time of the last warning for each user
user_warning_timestamps: Dict[int, float] = {}

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self, limit: int = 7, time_window: int = 10, warning_cooldown: int = 60):
        """
        Middleware for rate-limiting messages and callback queries (anti-flood).

        :param limit: Maximum number of events (messages + callbacks) allowed.
        :param time_window: Time window in seconds for counting events.
        :param warning_cooldown: Minimum interval in seconds between warnings for a user.
        """
        # defaultdict(list) to store timestamps for each user_id
        self.user_event_timestamps: Dict[int, List[float]] = defaultdict(list)
        self.limit = limit
        self.time_window = time_window
        self.warning_cooldown = warning_cooldown
        self.user_warning_timestamps = user_warning_timestamps
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        # Check if the event is a Message or CallbackQuery with a valid user
        if not isinstance(event, (Message, CallbackQuery)) or not event.from_user:
            logger.debug(f"Skipping event: {type(event).__name__} (no user or unsupported type)")
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.time()

        # Get the list of timestamps for the user
        timestamps = self.user_event_timestamps[user_id]

        # Remove timestamps older than the time window
        valid_timestamps = [ts for ts in timestamps if now - ts < self.time_window]

        # Add the current event's timestamp
        valid_timestamps.append(now)

        # Update the user's timestamp list
        self.user_event_timestamps[user_id] = valid_timestamps

        # Check if the event limit is exceeded
        if len(valid_timestamps) > self.limit:
            # Limit exceeded - potential flood
            last_warning_time = self.user_warning_timestamps.get(user_id, 0)

            # Check if we can send a warning (respecting cooldown)
            if now - last_warning_time > self.warning_cooldown:
                # Update the last warning time
                self.user_warning_timestamps[user_id] = now

                # Prepare warning message
                warning_message = (
                    f"❗️ Слишком много действий!\n"
                    f"({len(valid_timestamps)} событий за последние {self.time_window} сек).\n"
                    f"Пожалуйста, подождите. Следующее предупреждение через {self.warning_cooldown} сек."
                )

                try:
                    if isinstance(event, Message):
                        await event.answer(warning_message)
                    elif isinstance(event, CallbackQuery):
                        # Answer the callback to acknowledge it
                        await event.answer("Слишком много действий! Подождите.", show_alert=True)
                        # Send warning to the chat (if possible)
                        if event.message:
                            await event.message.answer(warning_message)
                except Exception as e:
                    logger.error(f"Failed to send warning to user {user_id}: {e}")

                logger.info(f"Flood detected for user {user_id}: {len(valid_timestamps)} events")
                return None  # Stop further processing

            else:
                # Warning was sent recently; silently ignore the event
                if isinstance(event, CallbackQuery):
                    try:
                        await event.answer()  # Acknowledge callback without alert
                    except Exception as e:
                        logger.debug(f"Failed to acknowledge callback for user {user_id}: {e}")
                return None  # Stop further processing

        # If limit is not exceeded, proceed with the handler
        return await handler(event, data)