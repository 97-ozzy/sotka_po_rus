from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.database import get_pool, get_premium_users
from handlers.base import menu
from keyboards.inline_kb import menu_and_buy_premium

router = Router()

@router.callback_query(F.data == 'stats')
async def user_stats(callback: CallbackQuery):
    premium_users = await get_premium_users()
    if callback.from_user.id not in premium_users:
        await callback.message.answer('Личная статистика доступна только премиум пользователям',
                                      reply_markup=menu_and_buy_premium())
        await callback.answer()
        return
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT task_number, total_attempts, correct_attempts, longest_streak
            FROM user_task_stats
            WHERE user_id = $1
            ORDER BY task_number;
            """,
            callback.from_user.id
        )

    if not rows:
        await callback.message.answer("У вас пока нет статистики. Попробуйте решать задания через /practice 🎯")
        return

    text = "📊 Ваша статистика по заданиям:\n\n"
    for row in rows:
        task_number = row["task_number"]
        total = row["total_attempts"]
        correct = row["correct_attempts"]
        streak = row["longest_streak"]
        accuracy = (correct / total) * 100 if total else 0
        text += (
            f"➤ №{task_number}\n"
            f"  - Решено: {total}\n"
            f"  - Верных: {correct}\n"
            f"  - Точность: {accuracy:.1f}%\n"
            f"  - Самая длинная серия: {streak}\n\n"
        )

    await callback.message.edit_text(text)
    await menu(callback.message)
