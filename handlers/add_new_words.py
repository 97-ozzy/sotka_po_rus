from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database.database import get_pool
from config import ADMIN_IDS

router = Router()

@router.message(Command("add_new_words"))
async def ask_to_migrate_words(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас нет доступа к этой команде.")
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        submissions = await conn.fetch("""
            SELECT task_number, correct_word, incorrect_words 
            FROM word_submissions 
            WHERE status = 'approved'
        """)

    if not submissions:
        await message.answer("✅ Нет слов для миграции.")
        return

    count = len(submissions)
    preview_lines = []
    for sub in submissions:
        correct = sub['correct_word']
        incorrect = sub['incorrect_words']
        task = sub['task_number']
        preview_lines.append(f"• №{task}: «{correct}», «{incorrect}»")

    preview_text = "\n".join(preview_lines)
    text = f"📦 Найдено {count} слов для переноса:\n\n{preview_text}"

    # Ограничим длину сообщения Telegram'ом (4096 символов)
    if len(text) > 100:
        text = text[:100] + "\n...\n(список обрезан)"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"✅ Перенести {count} слов", callback_data="confirm_migrate")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_migrate")]
    ])

    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data == "confirm_migrate")
async def confirm_migration(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in ADMIN_IDS:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return

    pool = await get_pool()
    async with pool.acquire() as conn:
        submissions = await conn.fetch("""
            SELECT task_number, correct_word, incorrect_words 
            FROM word_submissions 
            WHERE status = 'approved'
        """)

        count = 0
        for sub in submissions:
            answer_options = [sub['correct_word']] + sub['incorrect_words'].split(',')
            await conn.execute("""
                INSERT INTO questions (task_number, answer_options, correct_answer)
                VALUES ($1, $2, $3)
            """, sub['task_number'], answer_options , sub['correct_word'])
            count += 1

        await conn.execute("""
            DELETE FROM word_submissions 
            WHERE status = 'approved'
        """)

    await callback.message.edit_text(f"✅ Перенос завершён. Добавлено {count} слов.")

@router.callback_query(F.data == "cancel_migrate")
async def cancel_migration(callback: CallbackQuery):
    await callback.message.edit_text("❌ Перенос отменён.")
