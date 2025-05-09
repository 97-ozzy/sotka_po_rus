import datetime

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link

from config import DAILY_REFERRED_NUMBER, \
    MONTHLY_REFERRED_NUMBER
from database.database import update_premium_expiration, get_expiring_date, count_users_referred_by, \
    get_referral_activations, update_referral_activation, update_premium_status
from keyboards.inline_kb import referral_system_keyboard, \
    referral_activation

router = Router()


@router.callback_query(F.data == 'referral_system')
async def referral_info(callback: CallbackQuery):
    referral_link = await create_start_link(callback.bot, str(callback.from_user.id))
    await callback.message.edit_text('Хочешь *бесплатный премиум* ? 💎\n\n'
                                     f'🔗 Вот твоя реферальная ссылка: `{referral_link}`\n\n'
                                     f'😉 За каждых {DAILY_REFERRED_NUMBER} друзей ты получаешь *+1 день премиума*! Даже, если он у тебя уже есть!\n\n'
                                     f'😁 Пригласив {MONTHLY_REFERRED_NUMBER} человек, ты получишь *премиум на месяц*!',
                                     reply_markup=referral_system_keyboard(),
                                     parse_mode='Markdown')

    
@router.callback_query(F.data == 'activate_premium')
async def activate_premium(callback: CallbackQuery):
    user_id = callback.from_user.id
    referred_users_count = await count_users_referred_by(user_id)
    month_activation, day_activation = await get_referral_activations(user_id)
    get_premium_days = referred_users_count//DAILY_REFERRED_NUMBER - day_activation
    get_premium_month = referred_users_count//MONTHLY_REFERRED_NUMBER - month_activation
    text = f'По твоей ссылке перешли: *{referred_users_count} человек*\n'
    text+= f'😎 Ты уже активировал премиум на {day_activation} день/дней.\n' if day_activation >0 else ''
    text+= f'😎 Ты уже активировал премиум на {month_activation} месяц/месяцев.\n' if month_activation >0 else ''
    text+= f'\n🤩 Ты можешь активировать премиум на {get_premium_days} день/дней\n' if get_premium_days >0 else ''
    text+= f'\n🤩 Ты можешь активировать премиум на {get_premium_month} месяц/месяцев' if get_premium_month > 0 else ''
    await callback.message.edit_reply_markup()
    await callback.message.answer(text=text,
                                  reply_markup=referral_activation(get_premium_days, get_premium_month),
                                  parse_mode='Markdown')

@router.callback_query(F.data.startswith('activate_ref_'))
async def activate_premium_day_month(callback: CallbackQuery):
    activation_type = callback.data.split('_')[2]
    amount =int(callback.data.split('_')[3])
    user_id = callback.from_user.id

    await update_referral_activation(activation_type, amount, user_id)

    amount = amount if activation_type=='day' else amount*30

    old_expiring_date = await get_expiring_date(user_id)
    today = datetime.date.today()

    new_expiring_date = today + datetime.timedelta(days=amount) \
        if old_expiring_date <= today else old_expiring_date + datetime.timedelta(days=amount)

    await update_premium_expiration(user_id, new_expiring_date)
    await update_premium_status(user_id, True)
    await callback.message.answer(f'🥳 Премиум успешно активирован на {amount} дней 🥳')





