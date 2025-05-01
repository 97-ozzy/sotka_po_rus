from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TASKS

def menu_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")]
    ])
def menu_and_buy_premium():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="💎 Оформить премиум", callback_data="premium")]
    ])
def send_bill_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="🧾 Отправить чек", callback_data="send_bill")]
    ])

def task_keyboard():
    inline_keyboard = [[InlineKeyboardButton(text="🏠 Меню", callback_data="menu")]]
    tasks= TASKS
    row = []
    for i, num in enumerate(tasks, 1):
        row.append(InlineKeyboardButton(text=f"№{num}", callback_data=f"task_{num}"))
        if i % 3 == 0:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Написать в поддержку", callback_data="support")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(text="🏆 Таблица лидеров", callback_data="leaderboard")],
        [InlineKeyboardButton(text="💎 Премиум-возможности", callback_data="premium")],
        [InlineKeyboardButton(text="🆕 Добавить свои слова", callback_data="submit")],
        [InlineKeyboardButton(text="💪 Приступить к практике", callback_data="start_practice")]
    ])

def explain_wrong_answer_keyboard(task_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
         InlineKeyboardButton(text="🆕 Выбрать задание", callback_data="practice")],

        [InlineKeyboardButton(text="🔁 Начать заново", callback_data="repeat_task"),
        InlineKeyboardButton(text="💡 Объясни", callback_data=f"explain_{task_id}")]
    ])
def wrong_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
            InlineKeyboardButton(text="🆕 Выбрать задание", callback_data="practice")],
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data="repeat_task")]
    ])
def buy_premium_wrong_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
         InlineKeyboardButton(text="🆕 Выбрать задание", callback_data="practice")],
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data="repeat_task")],
        [InlineKeyboardButton(text="💎 Оформить премиум", callback_data=f"premium")]
    ])

def moderation_keyboard(sub_id, user_id, correct_word):
    return  InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{sub_id}_{user_id}_{correct_word}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{sub_id}_{user_id}_{correct_word}")
        ],
        [InlineKeyboardButton(text="🚪 Выход", callback_data="moderation_exit")]
    ])

def buy_premium_keyboard():
    return  InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Купить Премиум за 20₽",
                    callback_data="buy_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Поддержать проект ❤️",
                    callback_data="support_project"
                )
            ],
            [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")]
        ]
    )