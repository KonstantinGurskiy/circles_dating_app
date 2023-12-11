from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    user_id = State()
    name = State()
    latitude = State()
    longitude = State()
    target = State()
    circle = State()
    likes = State()
    liked = State()
