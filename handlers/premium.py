import time
import logging
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from database.database import submit_payment, get_premium_users
from keyboards.inline_kb import send_bill_keyboard
from aiogram.exceptions import TelegramBadRequest

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = Router()

PREMIUM_PRICE_RUB = 20
ALLOWED_FILE_TYPES = ['photo', 'document']  # Допустимые типы файлов
ALLOWED_DOCUMENT_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png']  # Допустимые расширения для документов
TIMEOUT_SECONDS = 7*60  # Время ожидания чека (5 минут)


class BuyPremiumStates(StatesGroup):
    waiting_for_bill = State()


@router.callback_query(F.data == 'premium')
async def premium(callback: CallbackQuery):
    user_id = callback.from_user.id
    premium_status = await get_premium_users()
    text = "🌟 *Премиум-подписка* 🌟\n\n"
    text += '*Поздравляю 🎉🎉🎉 У тебя уже есть премиум* 😊\n' if user_id in premium_status else \
        'Получи больше возможностей для подготовки:\n'
    text += (
        "• Пояснения к ответам 📚\n"
        "• Подробная статистика по каждому заданию 📈\n\n"
        f"Стоимость — *{PREMIUM_PRICE_RUB} рублей в месяц* 💎\n\n"
        "Также ты можешь *поддержать проект* любой суммой ❤️\n\n"
        "Для оплаты нажми ниже:\n"
        "[Оплатить](https://www.tinkoff.ru/rm/r_klyTPqTGBH.jaDfOaXBit/Kacre89102)\n\n"
        "После оплаты отправь боту скриншот или файл чека (PDF, JPG, PNG)."
    )
    try:
        await callback.message.edit_text(
            text, reply_markup=send_bill_keyboard(), parse_mode="Markdown", disable_web_page_preview=True
        )
    except TelegramBadRequest as e:
        logger.error(f"Ошибка при редактировании сообщения: {e}")
        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуй снова.", reply_markup=send_bill_keyboard()
        )


@router.callback_query(F.data == 'send_bill')
async def send_bill(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BuyPremiumStates.waiting_for_bill)
    await callback.message.answer(
        "📸 Пожалуйста, отправь скриншот или файл чека (PDF, JPG, PNG).\n"
        f"У тебя есть {TIMEOUT_SECONDS // 60} минут, чтобы отправить чек."
    )
    # Устанавливаем таймер для очистки состояния
    await state.update_data(start_time=time.time())


@router.message(BuyPremiumStates.waiting_for_bill)
async def get_bill(message: Message, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username
    state_data = await state.get_data()
    start_time = state_data.get('start_time', time.time())

    # Проверка таймаута
    if time.time() - start_time > TIMEOUT_SECONDS:
        await message.answer(
            "⏰ Время ожидания чека истекло. Пожалуйста, начни процесс оплаты заново."
        )
        await state.clear()
        return

    # Проверка на наличие фото или документа
    if not (message.photo or message.document):
        await message.answer(
            "❌ Пожалуйста, отправь скриншот чека или файл (PDF, JPG, PNG).\n"
            "Попробуй снова."
        )
        return

    # Проверка типа документа
    if message.document:
        file_name = message.document.file_name.lower()
        if not any(file_name.endswith(ext) for ext in ALLOWED_DOCUMENT_EXTENSIONS):
            await message.answer(
                "❌ Неверный формат файла. Пожалуйста, отправь файл в формате PDF, JPG или PNG."
            )
            return

    # Получение file_id
    file_id = message.photo[-1].file_id if message.photo else message.document.file_id

    try:
        # Сохранение чека в базе данных
        await submit_payment(user_id,username, file_id)
        await message.answer(
            "✅ Спасибо! Чек принят. Если всё верно, скоро получишь премиум-доступ 💎"
        )
        logger.info(f"Чек успешно обработан для пользователя {user_id}, file_id: {file_id}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении чека для пользователя {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при обработке чека. Пожалуйста, попробуй снова или свяжитесь с поддержкой."
        )
    finally:
        await state.clear()

