from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database.database import submit_new_word, approve_new_submission, reject_new_submission, \
    get_pending_submission
from fsm import Moderation
from keyboards.inline_kb import moderation_keyboard

router = Router()

ADMIN_IDS = [936290830]



@router.message(Command('submit'))
async def submit_word(message: types.Message, state: FSMContext):
    await state.set_state(Moderation.waiting_for_word)
    await message.reply(
        "Пожалуйста, отправьте в формате:\n"
        "(номер задания) (правильное слово) (неправильные написания)\n"
        "Например:\n9 брошюра брошура\n"
        "Например:\n4 киоскЕр киОскер\n",
        parse_mode="Markdown"
    )

@router.message(Moderation.waiting_for_word)
async def process_submission(message: Message, state: FSMContext):
    user_id = message.from_user.id
    content = message.text.strip()

    try:
        parts = content.split()
        if len(parts) < 3:
            raise ValueError("❗ Недостаточно данных: укажите номер задания, правильное слово и хотя бы одно неправильное.")

        task_number = int(parts[0])
        correct_word = parts[1]
        incorrect_words_raw = ' '.join(parts[2:])
        incorrect_words = [w.strip() for w in incorrect_words_raw.replace(',', ' ').split()]

        if not correct_word.isalpha():
            raise ValueError("❗ Правильное слово должно содержать только буквы.")

        for word in incorrect_words:
            if not word.isalpha():
                raise ValueError(f"❗ Недопустимый вариант: '{word}' — только буквы.")

        incorrect_words_str = ', '.join(incorrect_words)

    except ValueError as e:
        return await message.reply(f"{str(e)}\nПопробуйте снова.")

    try:
        await submit_new_word(user_id, task_number, correct_word, incorrect_words_str)

        await message.reply(
            f"🔄️ Отправлено на модерацию\n"
            f"📚 Задание {task_number}: <b>{correct_word}</b>\n"
            f"❌ Ошибки: <i>{incorrect_words_str}</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply(f"⚠️ Ошибка при сохранении: {str(e)}")
    finally:
        await state.clear()
        


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
    

