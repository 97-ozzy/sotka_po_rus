from aiogram import Bot, Dispatcher
import asyncio

from database.database import init_dbs
from handlers import register_all_handlers
import os
from dotenv import load_dotenv
load_dotenv('utils/.env')

TOKEN = os.getenv("BOT_TOKEN")

async def main():
    init_dbs()

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    register_all_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())