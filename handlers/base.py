from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardRemove

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я помогу тебе подготовиться к ЕГЭ по русскому языку.\nВыбери команду:\n\n Приступить к практике - /practice",
        reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def help(message: Message):
    await message.answer("Вопросы по русскому языку? Я помогу!")
