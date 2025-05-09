import asyncio

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputFile
from aiogram.filters import Command, CommandStart, CommandObject

from config import ADMIN_IDS, RENEWAL_RETURN_URL
from database.database import add_user_to_db, clear_cache, get_pool, get_nonactive_users
from fsm import SendToEveryone
from keyboards.inline_kb import menu_keyboard, menu_button

router = Router()
@router.message(CommandStart(deep_link=True))
async def start(message: Message, command: CommandObject):
    user_id = message.from_user.id
    username = message.from_user.username
    referral_code = command.args
    
    await add_user_to_db(user_id, username)
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
        "📚 *Каждое новое добавленное слово улучшает твою подготовку!*",
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
#----------------------------------------
@router.message(Command('clear_cache'))
async def clear_cache_handler(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await clear_cache()
    await message.answer('Кэш очистен')

@router.message(Command('send_to_everyone'))
async def send_message_everyone(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer('Укажите промежуток дней, которые пользователь не заходил (два числа через пробел):\n'
                         'Например: 2 9 означает, что рассылка будет отправлена пользователям,'
                         'которые последний рза заходили в бота в от 2 до 9 дней назад.'
                         '0 означаете сегодня', reply_markup=menu_button())
    await state.set_state(SendToEveryone.waiting_for_interval)
    
    
@router.message(SendToEveryone.waiting_for_interval)
async def handle_interval(message: Message, state: FSMContext):
    try:
        start_day, end_day = map(int, message.text.split())
    except Exception as e:
        await message.answer(f'Ошибка в формате, начните сначала: ❗{e}')
        await state.clear()
        return
    await message.answer('Жду сообщение для рассылки...', reply_markup=menu_button())
    await state.update_data(start_day=start_day, end_day=end_day)
    await state.set_state(SendToEveryone.waiting_for_message)

@router.message(SendToEveryone.waiting_for_message)
async def handle_sending_message(message: Message, state: FSMContext):
    photo = message.photo
    text =message.caption if photo else message.text
    data = await state.get_data()
    start_day = data['start_day']
    end_day = data['end_day']
    users = await get_nonactive_users(start_day, end_day)

    if not users:
        return
    bot = message.bot

    success_count = 0
    failed_count = 0
    for user in users:
        #print(user['user_id'])
        try:
            if photo:
                #print(photo[-1].file_id)
                await bot.send_photo(
                chat_id=int(user['user_id']),
                photo=photo[-1].file_id,
                caption=text,
                parse_mode='Markdown'
                )
            else:
                await bot.send_message(
                    chat_id=int(user['user_id']),
                    text=text,
                    parse_mode='Markdown')
            success_count += 1
            await asyncio.sleep(0.5)

        except TelegramForbiddenError:

            await bot.send_message(ADMIN_IDS[0], f"🚫 Пользователь {user['user_id']} заблокировал бота")
            failed_count += 1

        except Exception as e:
            #await bot.send_message(ADMIN_IDS[0], f"⚠️ Ошибка при отправке пользователю {user['user_id']}: {str(e)}")
            failed_count += 1

    await bot.send_message(ADMIN_IDS[0],
                           f"📊 Итог: успешно отправлено {success_count}, не удалось отправить {failed_count}")
    await state.clear()
