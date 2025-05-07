import asyncio
from datetime import date, datetime
from aiogram import Bot
import logging

from database.database import get_expiring_premium_users, update_premium_status


async def remove_expired_premium(bot: Bot):
    today = date.today()
    expiring_users = await get_expiring_premium_users(today)

    if not expiring_users:
        logging.info("Нет пользователей с истекающей подпиской.")
        return

    for user in expiring_users:
        user_id = user["user_id"]
        try:
            await update_premium_status(user_id, False)
            await bot.send_message(
                chat_id=user_id,
                text="❗ Уведомление ❗\n"
                     "Премиум-подписка закончилась 😢\n"
                     "Ты сможете оформить ее в разделе:\n 💎 Премиум-возможности 😉"
            )
            logging.info(f"Уведомление отправлено пользователю {user_id}")
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")


# Функция для планирования ежедневного запуска в 18:00
async def schedule_notifications(bot: Bot):
    """Запускает уведомления каждый день в 18:00."""
    while True:
        now = datetime.now()
        target_time = now.replace(hour=16, minute=00, second=0, microsecond=0)

        # Если текущее время уже прошло 18:00, планируем на следующий день
        if now > target_time:
            target_time = target_time.replace(day=target_time.day + 1)

        # Вычисляем, сколько секунд нужно ждать до 18:00
        wait_seconds = (target_time - now).total_seconds()

        # Ждем до нужного времени
        await asyncio.sleep(wait_seconds)

        # Запускаем уведомления
        try:
            await remove_expired_premium(bot)
        except Exception as e:
            logging.error(f"Ошибка при выполнении уведомлений: {e}")