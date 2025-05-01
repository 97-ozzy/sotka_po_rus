from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import TASKS
from database.database import get_pool
from handlers.base import menu

router = Router()

@router.callback_query(F.data == 'leaderboard')
async def show_leaderboard(callback: CallbackQuery):
    leaderboard_text= ''
    conn = await get_pool()
    for task_number in TASKS:
        leaderboard_text += f"🏆 №{task_number}:\n"
        rows = await conn.fetch(
            """
            SELECT username, longest_streak
            FROM user_task_stats
            WHERE task_number = $1
            ORDER BY longest_streak DESC
            LIMIT 10;
            """,
            task_number
        )

        if not rows:
            await callback.message.answer(f"Пока нет данных для задания №{task_number}.")
        else:
            for i, row in enumerate(rows, 1):
                leaderboard_text += f"@{row['username']} — {row['longest_streak']} \n"
        leaderboard_text+='\n'

    await callback.message.edit_text(leaderboard_text)
    await callback.answer()
    await menu(callback.message)