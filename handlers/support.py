from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.database import get_pool
from fsm import SupportStates
from datetime import datetime

router = Router()



@router.message(Command("support"))
async def start_support(message: Message, state: FSMContext):
    await message.answer("✉️ Напишите своё сообщение, и мы обязательно прочитаем его!\n"
                         "_(Для выхода нажмите /menu)_", parse_mode='Markdown')
    await state.set_state(SupportStates.waiting_for_message)

@router.message(SupportStates.waiting_for_message)
async def receive_support_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    timestamp = datetime.now()

    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO support_messages (user_id, message, date)
            VALUES ($1, $2, $3)
        """, user_id, text, timestamp)

    await message.answer("✅ Ваше сообщение сохранено. Спасибо за обратную связь!")
    await state.clear()
