from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import TASKS
from database.database import submit_new_word
from fsm import Moderation
from handlers.base import menu
from keyboards.inline_kb import menu_button

router = Router()


@router.callback_query(F.data == 'submit')
async def submit_word(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Moderation.waiting_for_word)
    await callback.message.edit_text(
        "📝 *Предлагайте свои слова для заданий 9-15*\n\n"
        "Пожалуйста, отправьте слова (можно несколько за один раз) в формате:\n"
        "`<номер задания>.<правильное слово>.<неправильное слово>`\n\n"
        "*Примеры:*\n"
        "`9.кастрюля.кострюля`\n"
        "`10.придать (форму).предать (форму)`\n"
        "`12.просит.просет`\n\n",reply_markup=menu_button(),
        parse_mode="Markdown"
    )


@router.message(Moderation.waiting_for_word)
async def process_submission(message: Message, state: FSMContext):
    user_id = message.from_user.id
    content = message.text.strip().lower()

    submissions = content.split('\n')  # Split the message by newlines to support multiple submissions
    successful_submissions = 0
    failed_submissions = []

    for submission in submissions:
        try:
            parts = submission.split('.')
            if len(parts) < 3:
                raise ValueError("❗ Формат должен быть: <номер задания>.<правильное слово>.<неправильное слово>")

            task_number = int(parts[0].strip())
            correct_word = parts[1].strip()
            wrong_word = parts[2].strip()

            if task_number not in TASKS:
                raise ValueError(f"❗ Номер задания должен быть одним из: {', '.join(map(str, TASKS))}")

            if correct_word == wrong_word:
                raise ValueError("❗ Слова должны отличаться друг от друга.")

            # Submit the valid word pair
            await submit_new_word(user_id, task_number, correct_word, wrong_word)
            successful_submissions+=1
        except ValueError as e:
            failed_submissions.append(f"{submission}: {str(e)}")
        except Exception as e:
            failed_submissions.append(f"{submission}: ⚠️ Ошибка при сохранении: {str(e)}")

    # Send feedback for successful submissions
    if successful_submissions > 0:
        await message.reply(
            f"🔄️ Отправлено на модерацию: {successful_submissions} слов",
            parse_mode="HTML"
        )

    # Send feedback for failed submissions
    if failed_submissions:
        await message.reply(
            f"❌ Ошибки:\n" + "\n".join(failed_submissions),
            parse_mode="HTML"
        )

    # Clear the state and go back to the main menu
    await state.clear()
    await menu(message)
