from aiogram.dispatcher.filters.state import State, StatesGroup


class LoginOperator(StatesGroup):
    state_ = State()


class LoginUser(StatesGroup):
    state_ = State()
