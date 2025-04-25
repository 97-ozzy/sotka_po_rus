from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("premium"))
async def premium(message: Message):
    await message.answer("Ждите обновления... 🤫")
