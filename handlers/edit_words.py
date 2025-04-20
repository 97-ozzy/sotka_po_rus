from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from database.database import get_pool
from config import ADMIN_IDS
from handlers.base import start
from fsm import WordEditState

router = Router()


# Обработчик команды для начала редактирования
@router.message(Command("edit_words"))
async def edit_words(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return

    await message.answer("Введите слово, которое хотите редактировать:")
    await state.set_state(WordEditState.awaiting_word_to_edit)


# Обработчик ввода слова для редактирования
@router.message(WordEditState.awaiting_word_to_edit)
async def process_edit_word(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return

    word_to_edit = message.text.strip().lower()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, correct_answer, answer_options FROM questions WHERE correct_answer = $1 ",
            word_to_edit
        )
    if not row:
        await message.answer("❌ Слово не найдено в базе.")
        await state.clear()
        return

    q_id, correct, incorrect = row

    await state.update_data(question_id=q_id)

    text = (f"📦 Найдено в базе:\n\n "
            f"Правильное: {correct}\n"
            f"Варианты: {incorrect}")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Изменить написание", callback_data="edit_correct_word")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_edit")],
    ])

    await message.answer(text, reply_markup=kb, parse_mode='HTML')
    # Переходим к следующему этапу редактирования




@router.callback_query(F.data == "edit_correct_word")
async def edit_correct_word(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    await callback.message.answer("Введите правильное написание и варианты:")
    await state.set_state(WordEditState.awaiting_new_correct_word)


@router.message(WordEditState.awaiting_new_correct_word)
async def process_new_correct_word(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return

    user_text = message.text.strip().lower()
    user_text=user_text.split()
    correct_ans, ans_options = user_text[0], user_text

    user_data = await state.get_data()
    q_id = user_data.get("question_id")

    if not q_id:
        await message.answer("❌ Не удалось найти старое правильное слово.")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT correct_answer FROM questions WHERE id = $1",
            q_id
        )

    if not row:
        await message.answer("❌ Старое слово не найдено в базе данных.")
        return

    print(correct_ans, ans_options, q_id)
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE questions SET correct_answer = $1, answer_options = $2 WHERE id = $3",
            correct_ans, ans_options, q_id)

    await message.answer(f"✅ Слово обновлено .")


    await state.clear()



@router.callback_query(F.data == "cancel_edit")
async def cancel_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await start(callback.message)
    await state.clear()
