from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.database import get_pool
from fsm import SupportStates
from datetime import datetime

from handlers.base import menu
from keyboards.inline_kb import menu_button

router = Router()



@router.callback_query(F.data == 'support')
async def start_support(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SupportStates.waiting_for_message)
    await state.update_data()
    await callback.message.edit_text(
        "✉️ Напишите своё сообщение, и мы обязательно прочитаем его!",
        reply_markup=menu_button(), parse_mode='Markdown')

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

    await message.answer("✅ Сообщение сохранено. Спасибо за обратную связь!")
    await state.clear()
    await menu(message)
