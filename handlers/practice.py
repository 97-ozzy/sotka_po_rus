import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from database.database import get_pool, get_random_task
from fsm import Practice
from handlers.base import start
from keyboards.inline_kb import task_keyboard, wrong_answer_keyboard
from keyboards.reply_kb import answer_keyboard

router = Router()

@router.message(F.text == "/practice")
async def practice(message: Message):
    await message.answer("Выберите номер задания: \n"
                         "№4 - ударения\n"
                         "№9 - гласные в корне\n"
                         "№10 - приставки\n"
                         "№12 - глаголы\n"
                         "№15 - Н и НН", reply_markup=task_keyboard())

@router.callback_query(F.data.startswith("task_"))
async def choose_task(callback: CallbackQuery, state: FSMContext):
    task_number = int(callback.data.split("_")[1])
    pool = await get_pool()
    result = await get_random_task(pool, task_number)

    if not result:
        await callback.answer("Задание не найдено.")
        return

    options, correct = result
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)

    await state.update_data(task_number=task_number, correct=correct, streak=0)
    await state.set_state(Practice.answering)

    label = "Выберите слово с правильным ударением:" if task_number == "4" else "Выберите слово с правильным написанием:"
    await callback.message.edit_text(f"Задание: №{task_number}")
    await callback.message.answer(label, reply_markup=answer_keyboard(shuffled_options))

@router.message(Practice.answering)
async def handle_answer(message: Message, state: FSMContext):

    data = await state.get_data()
    task_number = data["task_number"]
    correct_answer = data["correct"]
    user_choice = message.text
    streak = data.get("streak", 0)

    if user_choice == correct_answer:
        pool = await get_pool()
        result = await get_random_task(pool, task_number)
        options, correct = result
        shuffled_options = options.copy()
        random.shuffle(shuffled_options)
        await state.update_data(correct=correct, streak=streak + 1)

        await message.answer("✅ Верно!", reply_markup=answer_keyboard(shuffled_options))
    else:
        await message.answer("❌ Неверно.", reply_markup=ReplyKeyboardRemove())
        await message.answer(f"Правильный ответ: {correct_answer}\nПравильно подряд: {streak}", reply_markup=wrong_answer_keyboard())
        await state.update_data(streak=0)
        await state.set_state(Practice.waiting_restart)

@router.callback_query(F.data == "repeat_task")
async def repeat_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    task_number = data.get("task_number")

    if not task_number:
        await callback.message.answer("Сначала выбери задание через /practice")
        return

    pool = await get_pool()
    result = await get_random_task(pool, task_number)
    options, correct = result
    shuffled_options = options.copy()
    random.shuffle(shuffled_options)

    await state.update_data(correct=correct)
    await state.set_state(Practice.answering)

    label = "Выберите слово с правильным ударением:" if task_number == "4" else "Выберите слово с правильным написанием:"
    await callback.message.answer(label, reply_markup=answer_keyboard(shuffled_options))

@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await start(callback.message)
