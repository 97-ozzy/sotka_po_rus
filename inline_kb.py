from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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

def answer_keyboard(options):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=opt)] for opt in options],
        resize_keyboard=True
    )

def wrong_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data="repeat_task")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")]
    ])