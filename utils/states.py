from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    name = State()
    age = State()
    latitude = State()
    longitude = State()
    target = State()
    about = State()
    photo = State()
