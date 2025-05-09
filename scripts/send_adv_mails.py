import asyncio
from datetime import date, datetime
from aiogram import Bot
import logging

from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import  FSInputFile

from config import PATH_TO_PHOTOS, ADMIN_IDS
from database.database import get_expiring_premium_users, update_premium_status, get_nonactive_users
from keyboards.inline_kb import menu_and_support


#async def exams_are_soon(bot: Bot):

async def have_not_been_here_for_a_while(bot: Bot):

    users = await get_nonactive_users(2, 7)

    if not users:
        return

    success_count = 0
    failed_count = 0

    for user in users:
        try:
            await bot.send_photo(
                chat_id=int(user['user_id']),
                photo=FSInputFile(f'{PATH_TO_PHOTOS}/board_with_todo.jpg'),
                caption=(
                    '👋 Привет! Мы заметили, что ты уже давно не пользовался(ась) ботом.\n'
                    '📩 Расскажи, в чем причина и что нам стоит исправить/улучшить?\n'
                    '❤️ Это поможет нам стать еще лучше!\n'
                    '_(Пиши все что придет в голову)_'
                ),
                reply_markup=menu_and_support(), parse_mode='Markdown'
            )
            success_count += 1

            await asyncio.sleep(0.5)

        except TelegramForbiddenError:

            await bot.send_message(ADMIN_IDS[0], f"🚫 Пользователь {user['user_id']} заблокировал бота")
            failed_count += 1

        except Exception as e:
            await bot.send_message(ADMIN_IDS[0], f"⚠️ Ошибка при отправке пользователю {user['user_id']}: {str(e)}")
            failed_count += 1

    await bot.send_message(ADMIN_IDS[0], f"📊 Итог: успешно отправлено {success_count}, не удалось отправить {failed_count}")



# Функция для планирования ежедневного запуска в 18:00
async def schedule_mail_list(bot: Bot):
    """Запускает уведомления каждый день в 18:00."""
    import os
    while True:
        now = datetime.now()
        target_time = now.replace(hour=17, minute=0, second=0, microsecond=0)

        # Если текущее время уже прошло 18:00, планируем на следующий день
        if now > target_time:
            target_time = target_time.replace(day=target_time.day + 1)

        # Вычисляем, сколько секунд нужно ждать до 18:00
        wait_seconds = (target_time - now).total_seconds()

        # Ждем до нужного времени
        await asyncio.sleep(wait_seconds)

        # Запускаем уведомления
        try:
            await have_not_been_here_for_a_while(bot)
        except Exception as e:
            logging.error(f"Ошибка при выполнении уведомлений: {e}")