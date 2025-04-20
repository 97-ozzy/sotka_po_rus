from aiogram.fsm.state import State, StatesGroup

class Practice(StatesGroup):
    answering = State()
    waiting_restart = State()

class Moderation(StatesGroup):
    waiting_for_word = State()
    moderating = State()