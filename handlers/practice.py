import random
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from database.database import get_pool, get_random_task
from fsm import Practice
from handlers.base import start
from aiogram.filters import Command
from keyboards.inline_kb import task_keyboard, wrong_answer_keyboard
from keyboards.reply_kb import answer_keyboard

router = Router()

@router.message(Command("practice"))
async def practice(message: Message):
    await message.answer("Выберите номер задания: \n"
                         "№4 - ударения\n"
                         "№9 - гласные в корне\n"
                         "№10 - приставки\n"
                         "№11 - суффиксы \n"
                         "№12 - глаголы\n"
                         "№13 - НЕ слитно или раздельно\n"
                         "№14 - слитно или раздельно\n"
                         "№15 - Н и НН", reply_markup=task_keyboard())

@router.callback_query(F.data.startswith("task_"))
async def choose_task(callback: CallbackQuery, state: FSMContext):
    task_number = int(callback.data.split("_")[1])
    pool = await get_pool()
    result = await get_random_task(pool, task_number)

    if not result:
        await callback.answer("Задание не найдено.")
        return

    question, correct, wrong = result
    await state.update_data(task_number=task_number, correct=correct, streak=0)
    await state.set_state(Practice.answering)

    options = [correct, wrong]
    random.shuffle(options)

    label =  f"Что вставить вместо пропуска\n\n {question}" if task_number != 4 else "Выберите слово с правильным ударением:"

    await callback.message.edit_text(f"Задание: №{task_number}")
    await callback.message.answer(label, reply_markup=answer_keyboard(options))

@router.message(Practice.answering)
async def handle_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    task_number = data["task_number"]
    correct_answer = data["correct"]
    user_choice = message.text.strip()
    streak = data.get("streak", 0)

    if user_choice == correct_answer:
        pool = await get_pool()
        result = await get_random_task(pool, task_number)

        question, correct, wrong = result
        options = [correct, wrong]
        random.shuffle(options)
        await state.update_data(correct=correct, streak=streak + 1)

        label = f'✅ Верно!\n\n{question}' if task_number != 4 else '✅ Верно!'

        await message.answer(label, reply_markup=answer_keyboard(options))

    else:
        await message.answer("❌ Неверно.", reply_markup=ReplyKeyboardRemove())
        await message.answer(f"Правильный ответ: {correct_answer}\nПравильно подряд: {streak}",
                             reply_markup=wrong_answer_keyboard())
        await state.update_data(streak=0)
        await state.set_state(Practice.waiting_restart)

@router.callback_query(F.data == "repeat_task")
async def repeat_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    data = await state.get_data()
    task_number = data.get("task_number")

    pool = await get_pool()
    result = await get_random_task(pool, task_number)

    question, correct, wrong = result
    await state.update_data(correct=correct)
    await state.set_state(Practice.answering)

    options = [correct, wrong]
    random.shuffle(options)

    label = f"Что вставить вместо пропуска\n\n {question}" if task_number != 4 else "Выберите слово с правильным ударением:"

    await callback.message.answer(label, reply_markup=answer_keyboard(options))

@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await start(callback.message)
