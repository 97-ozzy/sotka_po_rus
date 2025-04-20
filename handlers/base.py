from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardRemove
from database.database import add_user_to_db

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user_to_db(user_id, username)
    await message.answer(
        "Привет! Я помогу тебе подготовиться к ЕГЭ по русскому языку.\nВыбери команду:\n\n Приступить к практике - /practice",
        reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def help_info(message: Message):
    await message.answer("Вопросы по русскому языку? Я помогу!")
