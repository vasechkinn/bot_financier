from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
    waiting_login = State()
    waiting_pass = State()
