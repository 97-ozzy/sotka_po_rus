from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart

from config import ADMIN_IDS
from database.database import add_user_to_db, clear_cache, get_pending_premium, set_premium_status, remove_bill_from_db
from fsm import Premium
from keyboards.inline_kb import menu_keyboard, premium_moderation_keyboard

router = Router()
@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user_to_db(user_id, username)
    await message.answer(
        'Привет! Я — твой помощник для подготовки к экзамену. '
        'Я помогу тебе с заданиями и дам полезные советы. ')
    await menu(message)

@router.message(Command('menu'))
async def menu(message: Message):
    try:
        await message.bot.edit_message_reply_markup(
            chat_id=message.chat.id,
            message_id=message.message_id - 1
        )
    except:
        pass
    await message.answer(
        "📚 *Каждое новое добавленное слово улучшает твою подготовку!*",
        parse_mode="Markdown", reply_markup=menu_keyboard())

@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.clear()
    await menu(callback.message)
#----------------------------------------
@router.message(Command('clear_cache'))
async def clear_cache_handler(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await clear_cache()
    await message.answer('Кэш очистен')



async def send_premium_to_admin(message: Message, row):
    sub_id, user_id, username, file, time = row

    text = (
        f"📝 *Заявка #{sub_id}*\n"
        f"⌚ Время {time}\n"
        f"🤖Пользователь @{username}"
    )

    try:
        print(f"Sending photo with file_id: {file}")  # Отладка
        await message.answer_photo(
            photo=file,
            caption=text,
            parse_mode="Markdown",
            reply_markup=premium_moderation_keyboard(sub_id, user_id, username)
        )
    except Exception as e:
        print(f"Unexpected error with file_id: {file}, error: {e}")
        await message.answer(f"❌ Неизвестная ошибка: {e}")



@router.message(Command('moderate_premium'))
async def moderate_premium_handler(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return None
    row = await get_pending_premium()
    if not row:
        return await message.reply("ℹ️ Нет заявок на премиум.")

    await state.set_state(Premium.moderating)
    return await send_premium_to_admin(message, row)


@router.callback_query(F.data.startswith("approve_"))
async def approve_premium(callback: CallbackQuery):
    sub_id, user_id, username = callback.data.split('_')[1:]
    user_id = int(user_id)
    sub_id = int(sub_id)
    await set_premium_status(sub_id, user_id)
    await clear_cache()
    await callback.message.answer(f'Премиум выдан @{username} {user_id}')



@router.callback_query(F.data.startswith("reject_"))
async def reject_premium(callback: CallbackQuery):
    sub_id, user_id, username = callback.data.split('_')[1:]
    sub_id = int(sub_id)
    user_id = int(user_id)
    await remove_bill_from_db(sub_id)
    await callback.message.delete()
    await callback.message.answer(f'Премиум отклонен @{username} {user_id}')