from aiogram import Router, F
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

router = Router()

@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Главное меню:", reply_markup=ReplyKeyboardRemove())
