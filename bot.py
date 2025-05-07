import asyncio
import logging

from aiogram import Bot, Dispatcher

from middlewares.active_users import ActivityTrackerMiddleware
from middlewares.antiflood import AntiSpamMiddleware
from middlewares.error_handler import ErrorHandlerMiddleware
from database.database import init_dbs
from handlers import register_all_handlers
from config import TOKEN, ADMIN_IDS
from logs.logging_config import setup_logging
from payments.check_expirinh_prems import schedule_notifications


async def setup_bot():
    #await init_dbs()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.message.middleware(AntiSpamMiddleware(2,1, 10))
    dp.update.middleware(ErrorHandlerMiddleware(bot, ADMIN_IDS))
    dp.message.middleware(ActivityTrackerMiddleware())

    await bot.delete_webhook(drop_pending_updates=True)

    register_all_handlers(dp)

    try:
        # Запускаем планировщик уведомлений
        asyncio.create_task(schedule_notifications(bot))
        # Запускаем обработку истекающих подписок
        # сделать
    except Exception as e:
        logging.error(f"Ошибка в основном цикле: {e}")

    return dp, bot


async def main():
    setup_logging()

    try:
        dp, bot = await setup_bot()

        await dp.start_polling(bot, skip_updates=True)

    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())
