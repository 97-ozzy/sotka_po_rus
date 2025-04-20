from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def task_keyboard():
    inline_keyboard = []
    tasks= [4,9,10]
    row = []
    for i, num in enumerate(tasks, 1):
        row.append(InlineKeyboardButton(text=f"№{num}", callback_data=f"task_{num}"))
        if i % 3 == 0:
            inline_keyboard.append(row)
            row = []
    if row:
        inline_keyboard.append(row)

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def wrong_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data="repeat_task")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")]
    ])

def moderation_keyboard(sub_id):
    return  InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"approve_{sub_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{sub_id}")
        ],
        [InlineKeyboardButton(text="🚪 Выход", callback_data="moderation_exit")]
    ])