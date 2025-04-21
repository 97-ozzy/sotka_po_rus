from aiogram import Bot, Dispatcher
import asyncio
from middlewares.antiflood import AntiFloodMiddleware
from database.database import init_dbs
from handlers import register_all_handlers

from config import TOKEN, ADMIN_IDS
from middlewares.error_handler import ErrorHandlerMiddleware
from logs.logging_config import setup_logging



async def main():
    await init_dbs()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.message.middleware(AntiFloodMiddleware(cooldown_seconds=0.6))
    dp.update.middleware(ErrorHandlerMiddleware(bot, ADMIN_IDS))

    await bot.delete_webhook(drop_pending_updates=True)

    register_all_handlers(dp)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    setup_logging()
    asyncio.run(main())