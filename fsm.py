from aiogram.fsm.state import State, StatesGroup

class Practice(StatesGroup):
    answering = State()
    waiting_restart = State()

class Moderation(StatesGroup):
    waiting_for_word = State()
    moderating = State()

class SupportStates(StatesGroup):
    waiting_for_message = State()

class SubmitWord(StatesGroup):
    wrong_format = State()

class BuyPremiumStates(StatesGroup):
    waiting_for_bill = State()

class Premium(StatesGroup):
    moderating = State()