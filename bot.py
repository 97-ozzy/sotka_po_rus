from aiogram import Bot, Dispatcher
import asyncio
from middlewares.antiflood import AntiFloodMiddleware
from database.database import init_dbs
from handlers import register_all_handlers

from config import TOKEN

async def main():
    await init_dbs()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()


    dp.message.middleware(AntiFloodMiddleware(cooldown_seconds=0.6))

    register_all_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())