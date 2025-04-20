from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardRemove
from database.database import add_user_to_db
from config import ADMIN_IDS

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user_to_db(user_id, username)
    await message.answer(
        "Выбери команду:\n "
        "💪 Приступить к практике  - /practice\n"
        "🆕 Добавить свое слоово  - /submit\n"
        "ℹ️ Справка о боте - /help",
        reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def help_info(message: Message):
    await message.answer("Мы постоянно улучшаем бота.\n"
                         "Новые номера, скоро будут доступны.")

@router.message(Command("ac"))
async def help_info(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ Нет доступа")
    await message.answer("/moderate\n\n"
                         "/add_new_words\n\n"
                         "/edit_words")
