from aiogram import Router, F
from aiogram.types import Message, user
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.builders import form_btn

from utils.closest_person import search_machine

router = Router()

@router.message(Command("go!"))
async def search_people(message: Message, state: FSMContext):
    closest_person = await search_machine(message.from_user.id)
    # print(closest_person)
    await message.answer("Татьяна(45): куплю пива за куни")
