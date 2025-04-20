from aiogram.fsm.state import State, StatesGroup

class Practice(StatesGroup):
    answering = State()
    waiting_restart = State()

class Moderation(StatesGroup):
    waiting_for_word = State()
    moderating = State()

class WordEditState(StatesGroup):
    awaiting_word_to_edit =State()
    awaiting_new_correct_word = State()
    awaiting_new_answers = State()