from aiogram import Router, F
from aiogram.types import Message, user
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.builders import form_btn

from utils.search_machine import closest_person
from utils.coord2loco import get_place
from data.database import DataBase

router = Router()

@router.message(Command("go", "like", "dislike"))
async def search_people(message: Message, state: FSMContext, db: DataBase):
    contr_person = await closest_person(message.from_user.id, db)
    if isinstance(contr_person, int):
        await message.answer("Пользователи кончились", reply_markup=form_btn(["/form", "/go"]))
    else:
        await message.answer_video_note(
        contr_person["circle"],
        )
        await message.answer("Имя: " + contr_person["name"] + "\nЦель: " + contr_person["target"] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", contr_person["latitude"], contr_person["longitude"])).split(',')[-4:-1]), reply_markup=form_btn(["/like", "/dislike"]))
        print(message.text)



