import json
import random
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from fsm import Practice
from inline_kb import task_keyboard, answer_keyboard, wrong_answer_keyboard

router = Router()

with open("data/questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

def register_handlers(dp):
    dp.include_router(router)

@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Привет! Я помогу тебе готовиться к ЕГЭ по русскому языку.\nВыбери команду:\n\n/practice",
        reply_markup=ReplyKeyboardRemove())

@router.message(F.text == "/practice")
async def practice(message: Message):
    await message.answer("Выберите номер задания:", reply_markup=task_keyboard())

@router.callback_query(F.data.startswith("task_"))
async def choose_task(callback: CallbackQuery, state: FSMContext):
    task = callback.data.split("_")[1]
    if task not in QUESTIONS:
        await callback.answer("Этого задания пока нет.")
        return

    question = random.choice(QUESTIONS[task])
    options = question.copy()
    random.shuffle(options)


    await state.update_data(task_number=task, correct=question[0], streak=0)
    await state.set_state(Practice.answering)

    label = "Выберите слово с правильным ударением:" if task == "4" else "Выберите слово с правильным написанием:"
    await callback.message.edit_text(f"Задание: №{task}")
    await callback.message.answer(label, reply_markup=answer_keyboard(options))

@router.message(Practice.answering)
async def handle_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    task_number = data["task_number"]
    correct_answer = data["correct"]
    user_choice = message.text
    streak = data.get("streak", 0)

    if user_choice == correct_answer:
        new_question = random.choice(QUESTIONS[task_number])
        new_options = new_question.copy()
        random.shuffle(new_options)

        await state.update_data(correct=new_question[0], streak=streak + 1)

        await message.answer("✅ Верно!", reply_markup=answer_keyboard(new_options))
    else:
        await message.answer("❌ Неверно.", reply_markup=ReplyKeyboardRemove())
        await message.answer(f" Правильный ответ: {correct_answer}\nПравильно подряд: {streak}", reply_markup=wrong_answer_keyboard())

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

    question = random.choice(QUESTIONS[task_number])
    options = question.copy()
    random.shuffle(options)

    await state.update_data(correct=question[0])
    await state.set_state(Practice.answering)

    label = "Выберите слово с правильным ударением:" if task_number == "4" else "Выберите слово с правильным написанием:"
    await callback.message.answer(label, reply_markup=answer_keyboard(options))

@router.callback_query(F.data == "menu")
async def to_menu(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await start(callback.message)