from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TASKS

def menu_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")]
    ])

def menu_and_support():
    return InlineKeyboardMarkup(inline_keyboard=[
       [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="✉️ Написать в поддержку", callback_data="support")]
    ])

def menu_and_buy_premium():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="💎 ОФОРМИТЬ ПРЕМИУМ", callback_data="premium")]
    ])

def confirm_payment_button(url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить", url=url)],
        [InlineKeyboardButton(text="Подтвердить платеж", callback_data="confirm_payment")]
    ])

def send_bill_keyboard(user_id, premium_status):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="❤️ Поддержать", url="https://www.tinkoff.ru/rm/r_klyTPqTGBH.jaDfOaXBit/Kacre89102")],
        [InlineKeyboardButton(text="💳 Оплатить", callback_data="pay_terminal")],

    ]) if user_id not in premium_status else InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="❤️ Поддержать", url="https://www.tinkoff.ru/rm/r_klyTPqTGBH.jaDfOaXBit/Kacre89102")],
        [InlineKeyboardButton(text="😭 Отменить подписку", callback_data='delete_payment_data')]
    ])

#---------------------------------------------------------------------------------------------

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

#---------------------------------------------------------------------------------------------

def menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ Поддержка и информация", callback_data="info")],
        [InlineKeyboardButton(text="🏆 Список лидеров", callback_data="leaderboard")],
        [InlineKeyboardButton(text="📊 Моя статистика", callback_data="stats")],
        [InlineKeyboardButton(text="💎 Премиум-возможности", callback_data="premium")],
        [InlineKeyboardButton(text="🆕 Добавить свои слова", callback_data="submit")],
        [InlineKeyboardButton(text="💪 Приступить к практике", callback_data="start_practice")]
    ])


#---------------------------------------------------------------------------------------------

def explain_wrong_answer_keyboard(task_number, word):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
         InlineKeyboardButton(text="🆕 Выбрать задание", callback_data="practice")],

        [InlineKeyboardButton(text="💡 Объясни", callback_data=f"explain_{task_number}_{word}")],
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data=f"repeat_task")]
    ])
def wrong_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
            InlineKeyboardButton(text="🆕 Выбрать задание", callback_data="practice")],
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data=f"repeat_task")]
    ])
def buy_premium_wrong_answer_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu"),
         InlineKeyboardButton(text="🆕 Выбрать задание", callback_data="practice")],
        [InlineKeyboardButton(text="🔁 Начать заново", callback_data=f"repeat_task")],
        [InlineKeyboardButton(text="💎 Оформить премиум", callback_data=f"premium")]
    ])
#---------------------------------------------------------------------------------------------


def period_selection_keyboard():
    return  InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="По каждой неделе (PDF)", callback_data="period_pdf")],
        [InlineKeyboardButton(text="За все время", callback_data="period_all")],
        [InlineKeyboardButton(text="Предыдущая неделя", callback_data="period_previous")],
        [InlineKeyboardButton(text="Текущая неделя", callback_data="period_current")]
    ])
#---------------------------------------------------------------------------------------------

def info_support_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Политика конфиденциальности", url="https://telegra.ph/Politika-konfidencialnosti-dlya-Telegram-bota-Sotka-Po-Russkomu-05-07")],
        [InlineKeyboardButton(text="Пользовательское соглашение", url="https://telegra.ph/Polzovatelskoe-soglashenie-dlya-Telegram-bota-Sotka-Po-Russkomu-05-07")],
        [InlineKeyboardButton(text="🏠 Меню", callback_data="menu")],
        [InlineKeyboardButton(text="✉️ Написать в поддержку", callback_data="support")]
    ])

