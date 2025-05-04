from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def answer_keyboard(options):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=opt) for opt in options]],
        resize_keyboard=True
    )