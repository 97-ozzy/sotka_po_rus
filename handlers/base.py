from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.types import ReplyKeyboardRemove
from database.database import add_user_to_db
from config import ADMIN_IDS
from database.database import cache

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    await add_user_to_db(user_id, username)
    await message.answer(
        "📚 *Каждое новое добавленное слово улучшает твою подготовку!*\n\n"
        #"Выбери команду:\n "
        "💪 Приступить к практике  - /practice\n"
        "🆕 Добавить свое слово  - /submit\n"
        "🏆Таблица лидеров - /leaderboard\n\n"
        "✉️ Написать в поддержку - /support\n"
        "ℹ️ Справка о боте - /help",
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())

@router.message(Command("help"))
async def help_info(message: Message):
    await message.answer("✨ *Мы постоянно улучшаем бота!*\n\n"
        "Новые задания скоро появятся — следите за обновлениями.\n\n"
        "Если вы:\n"
        "• Нашли ошибку ❌\n"
        "• Хотите предложить идею 💡\n"
        "• Или у вас есть вопросы ❓\n\n"
        "Нажмите: /support\n"
        "_Мы всегда рады обратной связи!_\n"
        "_(Для выхода нажмите /start)_", parse_mode="Markdown")

@router.message(Command("admin_clear_cache"))
async def admin_clear_cache(message: Message):
    user_id = message.from_user.id
    if user_id not in ADMIN_IDS:
        return None
    global cache
    cache.clear()
    await message.answer("♻️ Кэш очищен.")
