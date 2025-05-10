from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from database.database import add_user_to_db
from keyboards.inline_kb import menu_keyboard

router = Router()
@router.message(CommandStart() )
async def start(message: Message, command: CommandObject):
    user_id = message.from_user.id
    username = message.from_user.username
    referral_code = command.args
    referral_code = int(referral_code) if referral_code else 0
    print(referral_code)
    await add_user_to_db(user_id, username, referral_code)
    await message.answer(
         'Привет! Я — твой помощник для подготовки к экзамену. Я помогу тебе с заданиями и дам полезные советы.\n\n'
        '🔖 ВСЕ слова из банка ФИПИ - проверенно экзаменаторами ЕГЭ\n'
        '🗒 LearnUp - система мотивации, не даст тебе позабыть о подготовке\n'
        '🤯 Spaced Repetition - система интервального повторения \n'
        '⚡️Блиц формат - не даст потерять интерес, почти как лента в тик токе\n'
        '💡Объяснения - правила в один клик, коротко и по факту\n'
        '📊 Статистика за неделю - она поможет отслеживать прогресс\n\n\n\n'
         '🥳*Первые 3 дня премиум бесплатно*🥳\n', parse_mode='Markdown'
         )
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
        "📚 *Добавляй свои слова, чтоб улучшить подготовку!*",
        parse_mode="Markdown", reply_markup=menu_keyboard())

@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery, state: FSMContext):
    try:
        await menu(callback.message)
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.clear()
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Message is already correct, no need to edit
            pass