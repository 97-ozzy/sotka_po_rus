from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TASKS


def task_keyboard(type):
    inline_keyboard = []
    tasks= TASKS
    row = []
    for i, num in enumerate(tasks, 1):
        row.append(InlineKeyboardButton(text=f"№{num}", callback_data=f"{type}_task_{num}"))
        if i % 3 == 0:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
def premium_wrong_answer_keyboard(text):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data="repeat_task")],
        [InlineKeyboardButton(text="🆕 Выбрать другое задание", callback_data="practice")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="Объяснить правило", callback_data=f"explain_{text}")]
    ])
def wrong_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data="repeat_task")],
        [InlineKeyboardButton(text="🆕 Выбрать другое задание", callback_data="practice")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")]
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
            ]
        ]
    )