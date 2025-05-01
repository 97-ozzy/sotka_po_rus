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
        "Пожалуйста, отправь слова (можно несколько за один раз) в формате:\n"
        "`<номер задания>.<правильное слово>.<неправильное слово>`\n\n"
        "*Примеры:*\n"
        "`9.кастрюля.кострюля`\n"
        "`10.придать (форму).предать (форму)`\n"
        "`12.просит.просет`\n\n"
        "Каждая пара слов должна быть на новой строке.",
        reply_markup=menu_button(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.message(Moderation.waiting_for_word)
async def process_submission(message: Message, state: FSMContext):
    user_id = message.from_user.id
    content = message.text

    if not content or not content.strip():
        await message.reply(
            "Вы отправили пустое сообщение. 🤷‍♂️\n"
            "Пожалуйста, используйте формат:\n"
            "`<номер>.<правильное>.<неправильное>`\n"
            "Каждая пара слов - на новой строке.",
             parse_mode="Markdown"
        )
        return

    submissions = content.strip().split('\n')
    successful_submissions_count = 0
    failed_submissions_details = []
    valid_tasks_str = ', '.join(map(str, TASKS))

    for submission in submissions:
        original_submission_text = submission
        submission = submission.strip()

        if not submission:
            continue

        try:
            parts = submission.split('.')
            if len(parts) < 3:
                raise ValueError("❗ Неверный формат строки. Ожидается `<номер>.<правильное>.<неправильное>`.")

            task_part = parts[0].strip()
            correct_word = parts[1].strip()
            wrong_word = ".".join(parts[2:]).strip()

            try:
                task_number = int(task_part)
            except ValueError:
                raise ValueError(f"❗ Номер задания '{task_part}' должен быть целым числом.")

            if task_number not in TASKS:
                raise ValueError(f"❗ Неверный номер задания '{task_number}'. Допустимые номера: {valid_tasks_str}.")

            if not correct_word or not wrong_word:
                raise ValueError("❗ Правильное и неправильное слова не могут быть пустыми.")

            if correct_word.strip().lower() == wrong_word.strip().lower():
                raise ValueError("❗ Правильное и неправильное слова должны отличаться.")

            await submit_new_word(user_id, task_number, correct_word, wrong_word)
            successful_submissions_count += 1

        except ValueError as e: # Ловим ожидаемые ошибки формата и валидации
            failed_submissions_details.append(f"❌ `{original_submission_text}`\n   ↳ {str(e)}")
        except Exception as e: # Ловим непредвиденные ошибки (например, с БД)
            failed_submissions_details.append(f"❌ `{original_submission_text}`\n   ↳ ⚠️ Произошла внутренняя ошибка при обработке этой строки.")

    reply_parts = []
    if successful_submissions_count > 0:
        reply_parts.append(f"✅ Успешно отправлено на модерацию: {successful_submissions_count} шт.")

    if failed_submissions_details:
        reply_parts.append(
            "❗️ Некоторые строки не удалось обработать из-за ошибок:\n\n" +
            "\n".join(failed_submissions_details) +
            "\n\nПожалуйста, исправь ошибки и попробуйте отправить эти строки снова.\n"
            "Напомню формат: `<номер>.<правильное>.<неправильное>`"
        )

    if not reply_parts:
         await message.reply(
            "Не найдено данных для обработки. 🤷‍♂️\n"
            "Пожалуйста, используй формат:\n"
            "`<номер>.<правильное>.<неправильное>`\n"
            "Каждая пара слов - на новой строке.",
             parse_mode="Markdown"
        )
    else:
        await message.reply("\n\n".join(reply_parts), parse_mode="Markdown")

    await state.clear()
    await menu(message)