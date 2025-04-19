from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command('moderation'))
async def moderation(message: Message):
    await message.answer("Отправьте слово для модерации.")
