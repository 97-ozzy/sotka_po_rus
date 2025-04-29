from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from database.database import add_user_to_db
from keyboards.inline_kb import menu_keyboard

router = Router()
@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user_to_db(user_id, username)
    await message.answer(
        'Привет! Я — твой помощник для подготовки к экзамену. '
        'Я помогу тебе с заданиями и дам полезные советы. '
        'Используй нажми на /menu для взаимодействия.')

@router.message(Command('menu'))
async def menu(message: Message):
    await message.answer(
        "📚 *Каждое новое добавленное слово улучшает твою подготовку!*",
        parse_mode="Markdown", reply_markup=menu_keyboard())

@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.clear()
    await menu(callback.message)

