import logging
import time
import uuid
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from yookassa import Configuration, Payment
from database.database import submit_payment, get_premium_users
from keyboards.inline_kb import send_bill_keyboard

# Настройка логирования
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

router = Router()

PREMIUM_PRICE_RUB = 40
ALLOWED_FILE_TYPES = ['photo']
ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']
TIMEOUT_SECONDS = 7 * 60

# Настройка YooKassa
Configuration.account_id = '1080022'
Configuration.secret_key = 'test_2rRoFU0aQ_TcGWpkqXG3VXrMzhgf8qzMGyi8IceADIU'


class BuyPremiumStates(StatesGroup):
    waiting_for_bill = State()
    waiting_for_payment_confirmation = State()


@router.callback_query(F.data == 'premium')
async def premium(callback: CallbackQuery, state: FSMContext):
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


@router.callback_query(F.data == 'pay_premium')
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
            "return_url": "https://t.me/test_sotkapr_bot"
        },
        "capture": True,
        "save_payment_method": True,
        "description": f"Премиум подписка для пользователя {user_id}",
        "metadata": {
            "user_id": str(user_id)
        }
    })

    # Сохранение ID платежа в состоянии
    await state.update_data(payment_id=payment.id)
    await state.set_state(BuyPremiumStates.waiting_for_payment_confirmation)

    payment_link = payment.confirmation.confirmation_url

    try:
        await callback.message.edit_text(
            f"Перейди по ссылке для оплаты:\n{payment_link}\n\n"
            "После оплаты вернись сюда и дождись подтверждения.",
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except TelegramBadRequest as e:
        logger.error(f"Ошибка при отправке ссылки на оплату: {e}")
        await callback.message.answer(
            "Произошла ошибка при создании платежа. Попробуй снова."
        )


@router.message(BuyPremiumStates.waiting_for_payment_confirmation)
async def check_payment_status(message: Message, state: FSMContext):
    user_id = message.from_user.id
    state_data = await state.get_data()
    payment_id = state_data.get('payment_id')

    if not payment_id:
        await message.answer("Ошибка: платеж не найден. Попробуй начать заново.")
        await state.clear()
        return

    # Проверка статуса платежа
    payment = Payment.find_one(payment_id)
    print(payment.status)

    if payment.status == "succeeded":
        # Обновление статуса премиум в базе данных
        print(user_id)

        await submit_payment(user_id, PREMIUM_PRICE_RUB, payment_id)

        await message.answer(
            "🎉 Оплата успешно подтверждена! Премиум-статус активирован!",
            parse_mode="Markdown"
        )
        await state.clear()
    elif payment.status == "canceled":
        await message.answer(
            "Оплата была отменена. Попробуй снова.",
            reply_markup=send_bill_keyboard(user_id, await get_premium_users())
        )
        await state.clear()
    else:
        await message.answer(
            "Платеж еще не обработан. Пожалуйста, подожди немного и попробуй снова."
        )