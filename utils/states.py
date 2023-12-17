from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    user_id = State()
    name = State()
    gender = State()
    look_for = State()
    latitude = State()
    longitude = State()
    target = State()
    circle = State()
    likes = State()
    liked = State()
    already_seen_by = State()
    already_saw = State()
    username = State()
    active = State()
