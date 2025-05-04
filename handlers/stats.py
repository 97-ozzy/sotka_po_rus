import datetime

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from database.database import get_pool, get_premium_users, get_week_start, get_previous_week_start
from handlers.base import menu
from keyboards.inline_kb import menu_and_buy_premium, period_selection_keyboard

router = Router()


@router.callback_query(F.data == 'stats')
async def user_stats(callback: CallbackQuery):
    await callback.answer()
    premium_users = await get_premium_users()
    if callback.from_user.id not in premium_users:
        await callback.message.edit_text('Личная статистика доступна только премиум пользователям',
                                      reply_markup=menu_and_buy_premium())
        await callback.answer()
        return

    try:
        await callback.message.edit_text("Выберите период для просмотра статистики:",
                                      reply_markup=period_selection_keyboard())
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Message is already correct, no need to edit
            pass


@router.callback_query(F.data == 'period_all')
async def handle_period_all(callback: CallbackQuery):
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
            await callback.message.answer("У тебя пока нет статистики. Попробуйте решать задания  🎯")
            return

        text = "📊 Статистика за все время:\n\n"
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

        try:
            await callback.message.edit_text(text)
            await menu(callback.message)
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                # Message is already correct, no need to edit
                pass

@router.callback_query(F.data == 'period_current')
async def handle_period_current(callback: CallbackQuery):
    await show_weekly_stats(callback, get_week_start())

@router.callback_query(F.data == 'period_previous')
async def handle_period_previous(callback: CallbackQuery):
    await show_weekly_stats(callback, get_previous_week_start())


async def show_weekly_stats(context: CallbackQuery | Message, week_start: datetime.date):
    if isinstance(context, CallbackQuery):
        message = context.message
        user_id = context.from_user.id
    else:
        message = context
        user_id = context.from_user.id
    week_end = week_start + datetime.timedelta(days=6)
    week_start_str = week_start.strftime("%d.%m.%y")
    week_end_str = week_end.strftime("%d.%m.%y")
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            '''
            SELECT task_number, attempts, correct
            FROM weekly_stats
            WHERE user_id = $1 AND week_start = $2
            ORDER BY task_number;
            ''',
            user_id, week_start
        )

    if not rows:
        await message.edit_text(f"Нет данных c *{week_start_str}* по *{week_end_str}*", parse_mode='Markdown')
        await menu(message)
        return

    text = f"📊 Статистика c *{week_start_str}* по *{week_end_str}*:\n\n"
    for row in rows:
        accuracy = (row['correct'] / row['attempts']) * 100 if row['attempts'] else 0
        text += f"№{row['task_number']}: {row['attempts']} попыток, {row['correct']} верно ({accuracy:.1f}%)\n\n"


    try:
        await message.edit_text(text, parse_mode='Markdown')
        await menu(message)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Message is already correct, no need to edit
            pass
