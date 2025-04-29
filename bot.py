import asyncio
from aiogram import Bot, Dispatcher
from middlewares.antiflood import AntiFloodMiddleware
from middlewares.error_handler import ErrorHandlerMiddleware
from database.database import init_dbs, check_cache_clear_flag
from handlers import register_all_handlers
from config import TOKEN, ADMIN_IDS
from logs.logging_config import setup_logging


async def setup_bot():
    #await init_dbs()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    #asyncio.create_task(check_cache_clear_flag())

    dp.message.middleware(AntiFloodMiddleware(cooldown_seconds=1))
    dp.update.middleware(ErrorHandlerMiddleware(bot, ADMIN_IDS))

    await bot.delete_webhook(drop_pending_updates=True)

    register_all_handlers(dp)

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
