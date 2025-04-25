from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import TASKS
from database.database import submit_new_word
from fsm import Moderation
from handlers.base import start

router = Router()

@router.message(Command('submit'))
async def submit_word(message: types.Message, state: FSMContext):
    await state.set_state(Moderation.waiting_for_word)
    await message.reply(
        "Предлагайте свои слова для заданий 9 - 15\n"
        "Пожалуйста, отправьте в формате:\n"
        "<номер задания>.<правильное слово>.<неправильное слово>\n\n"
        "Например:\n"
        "9.брошюра.брошура\n"
        "12.придать (форму).предать (форму)\n"
        "Чтоб выйти нажмите - /start",
        parse_mode="Markdown"
    )

@router.message(Moderation.waiting_for_word)
async def process_submission(message: Message, state: FSMContext):
    user_id = message.from_user.id
    content = message.text.strip().lower()

    try:
        parts = content.split('.')
        if len(parts) < 3:
            raise ValueError("❗ Формат должен быть: <номер задания>.<правильное слово>.<неправильное слово>")

        task_number = int(parts[0].strip())
        correct_word = parts[1].strip()
        wrong_word = parts[2].strip()

        if task_number not in TASKS:
            raise ValueError("❗ Номер задания должен быть одним из: 4, 9, 10, 11, 12, 13, 14, 15")

        if correct_word == wrong_word:
            raise ValueError("❗ Слова должны отличаться друг от друга.")

    except ValueError as e:
        return await message.reply(f"{str(e)}\nПопробуйте снова.")

    try:
        await submit_new_word(user_id, task_number, correct_word, wrong_word)

        await message.reply(
            f"🔄️ Отправлено на модерацию\n"
            f"📚 Задание {task_number}: <b>{correct_word}</b>\n",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply(f"⚠️ Ошибка при сохранении: {str(e)}")
    finally:
        await state.clear()
        await start(message)