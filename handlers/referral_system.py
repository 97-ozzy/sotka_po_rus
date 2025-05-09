import datetime
import logging
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link
from pyexpat.errors import messages
from reportlab.lib.pagesizes import elevenSeventeen
from yookassa import Configuration, Payment

from config import RENEWAL_RETURN_URL, PREMIUM_PRICE_RUB, UKASSA_TOKEN, SHOP_ID, DAILY_REFERRED_NUMBER, \
    MONTHLY_REFERRED_NUMBER
from database.database import get_premium_users, clear_cache, submit_payment, \
    update_premium_status, update_premium_expiration, get_expiring_date, count_users_referred_by, \
    get_referral_activations
from handlers.base import to_menu, menu
from keyboards.inline_kb import send_bill_keyboard, confirm_payment_button, menu_button, referral_system_keyboard, \
    referral_activation

router = Router()


@router.callback_query(F.data == 'referral_system')
async def referral_info(callback: CallbackQuery):
    referral_link = await create_start_link(callback.bot, str(callback.from_user.id))
    await callback.message.edit_text('Хочешь *бесплатный премиум* ? 💎\n\n'
                                     f'😉 За каждых {DAILY_REFERRED_NUMBER} друзей ты получаешь *+1 день премиума*! Даже, если он у тебя уже есть!\n\n'
                                     f'😁 Пригласив {MONTHLY_REFERRED_NUMBER} человек, ты получишь *премиум на месяц*!\n\n'
                                     f'🔗 Вот твоя реферальная ссылка: `{referral_link}`',
                                     reply_markup=referral_system_keyboard(),
                                     parse_mode='Markdown')

    
@router.callback_query(F.data == 'activate_premium')
async def activate_premium(callback: CallbackQuery):
    user_id = callback.from_user.id
    referred_users_count = await count_users_referred_by(user_id)
    month_activation, day_activation = await get_referral_activations(user_id)
    get_premium_days = referred_users_count//DAILY_REFERRED_NUMBER - day_activation
    get_premium_month = referred_users_count//MONTHLY_REFERRED_NUMBER - month_activation
    text = f'По твоей ссылке перешло/перешли: {referred_users_count} человек\n'
    text+= f'Ты можешь активировать премиум на {get_premium_days} день/дней.\n' if get_premium_days >0 else ''
    text+= f'Ты можешь активировать премиум на {get_premium_month} месяц/месяцев' if get_premium_month > 0 else ''
    await callback.message.edit_reply_markup()
    await callback.message.answer(text=text,
                                  reply_markup=referral_activation(get_premium_days, get_premium_month))
