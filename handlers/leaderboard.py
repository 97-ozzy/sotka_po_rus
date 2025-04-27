from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.database import get_pool
from keyboards.inline_kb import task_keyboard

router = Router()

@router.message(Command("leaderboard"))
async def leaderboard(message: Message):
    await message.answer(
        "Выберите номер задания для просмотра таблицы лидеров:",
        reply_markup=task_keyboard('leaderboard')
    )

# Обработчик нажатий на кнопки выбора задания
@router.callback_query(F.data.startswith("leaderboard_task_"))
async def show_leaderboard(callback: CallbackQuery):
    task_number = int(callback.data.split("_")[2])

    conn = await get_pool()
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
        leaderboard_text = f"🏆 Топ-10 по заданию №{task_number}:\n\n"
        for i, row in enumerate(rows, 1):
            leaderboard_text += f"№{i}. @{row['username']} — {row['longest_streak']} \n"

        await callback.message.answer(leaderboard_text)

    await callback.answer()