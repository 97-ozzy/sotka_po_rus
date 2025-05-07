import datetime
import logging
import time
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from yookassa import Configuration, Payment

from config import RENEWAL_RETURN_URL, PREMIUM_PRICE_RUB, UKASSA_TOKEN, SHOP_ID, ADMIN_IDS
from database.database import get_premium_users, clear_cache, submit_payment, \
    update_premium_status, update_premium_expiration, submit_payment_bill, get_pending_premium, remove_bill_from_db
from fsm import BuyPremiumStates, Premium
from handlers.base import to_menu
from keyboards.inline_kb import send_bill_keyboard, confirm_payment_button, premium_moderation_keyboard

# Настройка логирования
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

router = Router()


#ALLOWED_FILE_TYPES = ['photo']  # Допустимые типы файлов
#ALLOWED_DOCUMENT_EXTENSIONS = ['jpg', 'jpeg', 'png']  # Допустимые расширения для документов
TIMEOUT_SECONDS = 10*60

Configuration.account_id = SHOP_ID
Configuration.secret_key = UKASSA_TOKEN




@router.callback_query(F.data == 'premium')
async def premium(callback: CallbackQuery):
    user_id = callback.from_user.id
    premium_status = await get_premium_users()

    text = (
        '🌟 ПРЕМИУМ ПОДПИСКА 🌟\n\n'
        '📚 Пояснения к ответам - объяснения в один клик в самом удобном формате\n\n'
        '📊 Подробная статистика по каждому заданию - отслеживай свой прогресс\n\n'
        f'Стоимость - *всего {PREMIUM_PRICE_RUB} рублей в месяц* 💎\n\n'
        'Также ты можешь отправить любую сумму *на развитие проекта* ❤️\n\n'
    )
    text += "🎉 *У тебя есть премиум* 🎉" if user_id in premium_status else "Нажми кнопку ниже для оплаты."

    try:
        await callback.message.edit_text(
            text,
            reply_markup=send_bill_keyboard(user_id, premium_status),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            logger.error(f"Ошибка premium: {e}")
            await callback.message.answer(
                "Произошла ошибка. Пожалуйста, попробуй снова.",
                reply_markup=send_bill_keyboard(user_id, premium_status)
            )


@router.callback_query(F.data == 'pay_terminal')
async def initiate_payment(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # Создание платежа
    payment = Payment.create({
        "amount": {
            "value": f"{PREMIUM_PRICE_RUB}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": RENEWAL_RETURN_URL
        },
        "capture": True,
        "description": f"Разовый премиум-доступ для пользователя {user_id}",
        "metadata": {
            "user_id": str(user_id)
        }
    })

    # Сохранение ID платежа в состоянии
    await state.update_data(payment_id=payment.id)

    payment_link = payment.confirmation.confirmation_url

    try:
        await callback.message.edit_text(
            f"Нажмите оплатить\n\n"
            "После оплаты вернись сюда и нажмите подтвердить платеж.",
            parse_mode="Markdown", reply_markup=confirm_payment_button(payment_link)
        )
    except TelegramBadRequest as e:
        logger.error(f"Ошибка при отправке ссылки на оплату: {e}")
        await callback.message.answer(
            "Произошла ошибка при создании платежа. Попробуй снова."
        )


# @router.callback_query(F.data == 'donate_money')
# async def initiate_payment(callback: CallbackQuery, state: FSMContext):

@router.callback_query(F.data == 'confirm_payment')
async def check_payment_status(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    user_id = callback.from_user.id
    state_data = await state.get_data()
    payment_id = state_data.get('payment_id')

    if not payment_id:
        await message.answer("Ошибка: платеж не найден. Попробуй начать заново.")
        await state.clear()
        await premium(callback)
        return

    # Проверка статуса платежа
    payment = Payment.find_one(payment_id)

    if payment.status == "succeeded":
        # Обновление статуса премиум в базе данных
        #await submit_first_recurring_payment_info(user_id, payment.payment_method['id'])
        await update_premium_status(user_id, True)
        today = datetime.date.today()
        expire_date = today.replace(month=today.month + 1)
        await update_premium_expiration(user_id,expire_date )
        await submit_payment(user_id, PREMIUM_PRICE_RUB, datetime.datetime.now(), payment_id)
        await clear_cache()

        await message.edit_reply_markup()
        await message.answer(
            "🎉 *Оплата подтверждена. Премиум активирован!* 🎉",
            parse_mode="Markdown"
        )
        await to_menu(callback, state)
        await state.clear()
    elif payment.status == "canceled":
        await message.edit_reply_markup()
        await message.answer(
            "Оплата была отменена. Попробуй снова.",
            reply_markup=send_bill_keyboard(user_id, await get_premium_users())
        )
        await state.clear()
    else:
        await message.answer(
            "Платеж еще не обработан. Пожалуйста, подожди немного и попробуй снова."
        )


# @router.callback_query(F.data == 'send_bill')
# async def send_bill(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(BuyPremiumStates.waiting_for_bill)
#     await callback.message.answer(
#         "📸 Пожалуйста, отправь скриншот чека.\n"
#         f"У тебя есть {TIMEOUT_SECONDS // 60} минут, чтобы отправить чек."
#     )
#     # Устанавливаем таймер для очистки состояния
#     await state.update_data(start_time=time.time())


# @router.message(BuyPremiumStates.waiting_for_bill)
# async def get_bill(message: Message, state: FSMContext):
#     user_id = message.from_user.id
#     username = message.from_user.username
#     state_data = await state.get_data()
#     start_time = state_data.get('start_time', time.time())
#
#     # Проверка таймаута
#     if time.time() - start_time > TIMEOUT_SECONDS:
#         await message.answer(
#             "⏰ Время ожидания чека истекло. Пожалуйста, начни процесс оплаты заново."
#         )
#         await state.clear()
#         return
#
#     # Проверка на наличие фото или документа
#     if not message.photo:
#         await message.answer(
#             "❌ Пожалуйста, отправь скриншот чека.\n"
#             "Попробуй снова."
#         )
#         return
#
#
#     # Получение file_id
#     file_id = message.photo[-1].file_id
#
#     try:
#         # Сохранение чека в базе данных
#         await submit_payment_bill(user_id,username, file_id)
#         await message.answer(
#             "✅ Спасибо! Чек принят. Если всё верно, скоро получишь премиум-доступ 💎"
#         )
#         logger.info(f"Чек успешно обработан для пользователя {user_id}, file_id: {file_id}")
#     except Exception as e:
#         logger.error(f"Ошибка при сохранении чека для пользователя {user_id}: {e}")
#         await message.answer(
#             "😔 Произошла ошибка при обработке чека. Пожалуйста, попробуй снова или свяжитесь с поддержкой."
#         )
#     finally:
#         await state.clear()
#
# async def send_premium_to_admin(message: Message, row):
#     sub_id, user_id, username, file, time = row
#
#     text = (
#         f"📝 *Заявка #{sub_id}*\n"
#         f"⌚ Время {time}\n"
#         f"🤖Пользователь @{username}"
#     )
#
#     try:
#         print(f"Sending photo with file_id: {file}")  # Отладка
#         await message.answer_photo(
#             photo=file,
#             caption=text,
#             parse_mode="Markdown",
#             reply_markup=premium_moderation_keyboard(sub_id, user_id, username)
#         )
#     except Exception as e:
#         print(f"Unexpected error with file_id: {file}, error: {e}")
#         await message.answer(f"❌ Неизвестная ошибка: {e}")



# @router.message(Command('moderate_premium'))
# async def moderate_premium_handler(message: Message, state: FSMContext):
#     if message.from_user.id not in ADMIN_IDS:
#         return None
#     row = await get_pending_premium()
#     if not row:
#         return await message.reply("ℹ️ Нет заявок на премиум.")
#
#     await state.set_state(Premium.moderating)
#     return await send_premium_to_admin(message, row)
#
#
# @router.callback_query(F.data.startswith("approve_"))
# async def approve_premium(callback: CallbackQuery):
#     sub_id, user_id, username = callback.data.split('_')[1:]
#     user_id = int(user_id)
#     sub_id = int(sub_id)
#     await update_premium_status(user_id, True)
#     today = datetime.date.today()
#     expire_date = today.replace(month=today.month + 1)
#     await update_premium_expiration(user_id, expire_date)
#     await clear_cache()
#     await callback.message.answer(f'Премиум выдан @{username} {user_id}')
#
#
#
# @router.callback_query(F.data.startswith("reject_"))
# async def reject_premium(callback: CallbackQuery):
#     sub_id, user_id, username = callback.data.split('_')[1:]
#     sub_id = int(sub_id)
#     user_id = int(user_id)
#     await remove_bill_from_db(sub_id)
#     await callback.message.delete()
#     await callback.message.answer(f'Премиум отклонен @{username} {user_id}')