import logging
import random
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from database.database import get_pool, get_random_task, get_premium_users, get_week_start
from fsm import Practice
from handlers.base import to_menu
from keyboards.inline_kb import task_keyboard, wrong_answer_keyboard, \
    explain_wrong_answer_keyboard, buy_premium_wrong_answer_keyboard
from keyboards.reply_kb import answer_keyboard

router = Router()
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'start_practice')
async def practice(callback: CallbackQuery):
    try:
        await callback.message.edit_text("Выбери номер задания: \n"
                         "№4 - ударения\n"
                         "№9 - гласные в корне\n"
                         "№10 - приставки\n"
                         "№11 - суффиксы \n"
                         "№12 - глаголы\n"
                         #"№13 - НЕ слитно или раздельно\n"
                         #"№14 - слитно или раздельно\n"
                         "№15 - Н и НН", reply_markup=task_keyboard())
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass
        else:
            logger.error(f"Ошибка practice: {e}")

@router.callback_query(F.data.startswith("task_"))
async def choose_task(callback: CallbackQuery, state: FSMContext):
    current_state = await state.set_state(Practice.answering)
    if current_state == Practice.answering:
        return
    task_number = int(callback.data.split("_")[1])
    pool = await get_pool()
    result = await get_random_task(pool, task_number)

    if not result:
        await callback.answer("Задание не найдено.")
        return

    word, question, correct, wrong = result
    await state.update_data(task_number=task_number, word=word, correct=correct, streak=0)


    options = [correct, wrong]
    random.shuffle(options)
    options= options if task_number !=15 else ['н','нн']

    label =  f"Что вставить вместо пропуска\n\n {question}" if task_number != 4 else "Выбери слово с правильным ударением:"

    await callback.message.edit_text(f"Задание: №{task_number}")
    await callback.message.answer(label, reply_markup=answer_keyboard(options))

@router.message(Practice.answering)
async def handle_answer(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    data = await state.get_data()
    task_number = data["task_number"]
    correct_answer = data["correct"]
    word = data['word']
    user_choice = message.text.strip().lower() if task_number !=4 else message.text.strip()
    streak = data.get("streak", 0)
    pool = await get_pool()
    if user_choice == correct_answer:

        result = await get_random_task(pool, task_number)

        new_word, question, correct, wrong = result
        options = [correct, wrong]
        random.shuffle(options)
        options = options if task_number != 15 else ['н', 'нн']

        await state.update_data(correct=correct, streak=streak + 1, word=new_word)

        label = f'✅ Верно!\n\n{question}' if task_number != 4 else '✅ Верно!'

        await message.answer(label, reply_markup=answer_keyboard(options))

    else:
        username = message.from_user.username
        user_id = message.from_user.id
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    """
                    INSERT INTO user_task_stats (user_id, task_number, longest_streak, username)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id, task_number) DO UPDATE
                    SET 
                        longest_streak = GREATEST(user_task_stats.longest_streak, $3)
                    ;
                    """,
                    user_id, task_number, streak, username
                )


                week_start = get_week_start()

                await conn.execute('''
                                INSERT INTO weekly_stats (user_id, task_number, week_start, attempts, correct)
                                VALUES ($1, $2, $3, $4 + 1, $4)
                                ON CONFLICT (user_id, task_number, week_start)
                                DO UPDATE SET
                                    attempts = weekly_stats.attempts + $4 +1,
                                    correct = weekly_stats.correct + $4;
                            ''', user_id, task_number, week_start, streak)


        longest_streak_in_db = await pool.fetchval(
            """
            SELECT longest_streak FROM user_task_stats
            WHERE user_id = $1 AND task_number = $2;
            """,
            user_id, task_number
        )

        if streak >= longest_streak_in_db:
            record_text = "\n🏆 Новый рекорд!"
        else:
            record_text = ""

        await message.answer(
            "❌ Неверно", reply_markup=ReplyKeyboardRemove())
        text = (f"Правильный ответ: {word}\n\n"
                f"Правильных подряд ответов: {streak}{record_text}\n")

        await message.answer(text, reply_markup= explain_wrong_answer_keyboard(task_number, word))

        await state.update_data(streak=0)


@router.callback_query(F.data == "repeat_task")
async def repeat_task_handler(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass

    data = await state.get_data()
    task_number =  data.get('task_number')
    if task_number is None:
        await to_menu(callback, state)
        return

    pool = await get_pool()
    result = await get_random_task(pool, task_number)
    word, question, correct, wrong = result

    await state.update_data(correct=correct, word = word)
    await state.set_state(Practice.answering)

    options = [correct, wrong]
    random.shuffle(options)
    options = options if task_number != 15 else ['н', 'нн']

    label = f"Что вставить вместо пропуска\n\n {question}" if task_number !=4 else "Выбери слово с правильным ударением:"

    await callback.message.answer(label, reply_markup=answer_keyboard(options))



@router.callback_query(F.data == "practice")
async def select_another_task(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.clear()
        await practice(callback)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass


@router.callback_query(F.data.startswith("explain_"))
async def select_another_task(callback: CallbackQuery):
    premium_users = await get_premium_users()
    if callback.from_user.id not in premium_users:
        await callback.message.edit_reply_markup()
        await callback.message.answer('*Объяснения доступны только премиум пользователям*',
                                      parse_mode='Markdown',
                                      reply_markup=buy_premium_wrong_answer_keyboard())
        await callback.answer()
        return
    task_number, word = callback.data.split('_')[1:]
    task_number =int(task_number)
    current_text = callback.message.text
    pool = await get_pool()
    async with pool.acquire() as conn:
        explanation = await conn.fetchval(
        """
        SELECT explanation FROM questions
        WHERE task_number = $1 AND word = $2;
        """, task_number, word)
    explanation = explanation.replace('\\n', '\n')
    new_text = current_text + '\n\n' + explanation

    await callback.answer()
    try:
        await callback.message.edit_text(new_text, reply_markup=wrong_answer_keyboard(), parse_mode='Markdown')
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            pass