from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

from handlers.base import menu
from keyboards.inline_kb import buy_premium_keyboard

router = Router()


@router.message(Command("premium"))
async def premium(message: Message):
    text = (
        "🌟 *Премиум-подписка* 🌟\n\n"
        "Получите больше возможностей для подготовки:\n"
        "• Пояснения к ответам 📚\n"
        "• Подробная статистика по каждому заданию 📈\n\n"
        "Стоимость — *20 рублей в месяц* 💎\n\n"
        "Также вы можете *поддержать проект* любой суммой ❤️\n\n"
        "Выберите действие:"
    )

    await message.answer(text, reply_markup=buy_premium_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == 'buy_premium')
async def buy_premium(callback: CallbackQuery):
    await callback.message.edit_text('Пока не доступно 😢')
    await menu(callback.message)

@router.callback_query(F.data == 'support_project')
async def support_project(callback: CallbackQuery):
    await callback.message.edit_text('Пока не доступно 😢')
    await menu(callback.message)