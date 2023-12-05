from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.states import Form

router = Router()

@router.message(Command("form"))
async def my_form(message: Message):
    await state.set_state(Form.name)
    await message.answer("Отлично, введи своё имя: ")


@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set.state(Form.age)
    await message.answer("Теперь укажи свой возраст")


@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(age=int(message.text))
        await state.set_state(Form.city)
        await message.answer("Теперь укажи свой город")
    else:
        await message.answer("Попробуй еще раз!")

@router.message(Form.city)
async def form_city(message: Message, state: FSMContext):
    ...
