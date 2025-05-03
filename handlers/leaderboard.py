from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import TASKS
from database.database import get_pool
from handlers.base import menu

router = Router()

def blur_username(username):
    if username == None:
        return 'noname'
    encode = username[1:-1]
    encode = [encode[i] if i%2==0 else '*' for i in range(len(encode))]
    encode = ''.join(encode)
    encode = username[0]+encode+username[-1]
    return encode

@router.callback_query(F.data == 'leaderboard')
async def show_leaderboard(callback: CallbackQuery):
    username = callback.from_user.username
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
                username_added = f"@{row['username']}" if row['username']==username else blur_username(row['username'])
                leaderboard_text += f"{username_added} — {row['longest_streak']} \n"
        leaderboard_text+='\n'
    try:
        await callback.message.edit_text(leaderboard_text)
        await callback.answer()
        await menu(callback.message)
    except:
        pass