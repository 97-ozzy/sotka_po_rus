from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
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
        "9 брошюра брошура\n\n"
        "Чтоб выйти нажмите - /start",
        parse_mode="Markdown"
    )

@router.message(Moderation.waiting_for_word)
async def process_submission(message: Message, state: FSMContext):
    user_id = message.from_user.id
    content = message.text.strip().lower()

    try:
        parts = content.split()
        if len(parts) < 3:
            raise ValueError("❗ Недостаточно данных: укажите номер задания, правильное слово и хотя бы одно неправильное.")

        task_number = int(parts[0])
        correct_word = parts[1]
        incorrect_words_raw = ' '.join(parts[2:])
        incorrect_words = [w.strip() for w in incorrect_words_raw.replace(',', ' ').split()]

        if not correct_word.isalpha():
            raise ValueError("❗ Правильное слово должно содержать только буквы.")

        for word in incorrect_words:
            if not word.isalpha():
                raise ValueError(f"❗ Недопустимый вариант: '{word}' — только буквы.")

        incorrect_words_str = ','.join(incorrect_words)

    except ValueError as e:
        return await message.reply(f"{str(e)}\nПопробуйте снова.")

    try:
        await submit_new_word(user_id, task_number, correct_word, incorrect_words_str)

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