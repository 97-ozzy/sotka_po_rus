
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.database import approve_new_submission, reject_new_submission, get_pending_submission
from fsm import Moderation
from keyboards.inline_kb import moderation_keyboard
from config import ADMIN_IDS

router = Router()

@router.message(Command('moderate'))
async def start_moderation(message: Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return await message.reply("⛔ У вас нет прав для модерации")

    row = await get_pending_submission()
    if not row:
        return await message.reply("ℹ️ Нет заявок на модерацию.")

    await state.set_state(Moderation.moderating)
    await send_submission_to_admin(message, row)
    

async def send_submission_to_admin(message: Message, row):
    sub_id, user_id, task_number, correct_word, incorrect_words= row
    

    text = (
        f"📝 <b>Заявка #{sub_id}</b>\n"
        f"📚 Задание {task_number}\n"
        f"✅ <b>{correct_word}</b>\n"
        f"❌ <i>{incorrect_words}</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=moderation_keyboard(sub_id, user_id, correct_word))

@router.callback_query(lambda c: c.data.startswith("approve_") or c.data.startswith("reject_"))
async def handle_decision(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("⛔ Нет доступа")
    #print(callback.data.split("_"))
    action, sub_id, user_id, correct_word = callback.data.split("_")
    sub_id =int(sub_id)
    user_id=int(user_id)
    if action == "approve":

        await approve_new_submission(user_id, sub_id)
        try:
            await callback.bot.send_message(user_id,
                f"✅ Ваше слово *{correct_word}* принято и добавлено!",
                parse_mode="Markdown"
            )
        except:
            pass  # user might block the bot
    else:
        try:
            await callback.bot.send_message(user_id,
                f"❌ Ваше слово *{correct_word}* не одобрено!",
                parse_mode="Markdown"
            )
        except:
            pass
        await reject_new_submission(sub_id)

    await callback.message.edit_text("✅ Заявка обработана.")
    await callback.answer()

    # Показываем следующую заявку
    next_row = await get_pending_submission()
    if next_row:
        await send_submission_to_admin(callback.message, next_row)
    else:
        await callback.message.answer("ℹ️ Заявки закончились.")
        await state.clear()

@router.callback_query(lambda c: c.data == "moderation_exit")
async def exit_moderation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🚪 Модерация завершена.")
    await callback.answer()
    

