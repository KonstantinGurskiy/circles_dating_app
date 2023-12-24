from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from data.database import DataBase


from asyncio import sleep
from utils.coord2loco import get_place

router = Router()
db = DataBase("users_db.db", "users")

@router.message(Command("show"))
async def show_profile(message: Message, state: FSMContext, db: DataBase, bot: Bot):
    df = await db.read_table()
    data = df[df['user_id']==message.from_user.id].iloc[0]
    if(data["gender"]==None):
        await message.answer("Твое событие:")

        await message.answer_video_note(
            data["circle"],
        )
        await message.answer("Имя: " + data["name"] + "\nТы -- " + data["target"] + "\nПриглашаю: " + data["look_for"] + "\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]))
    else:
        await message.answer("Твой профиль:")

        await message.answer_video_note(
            data["circle"],
        )
        await message.answer("Имя: " + data["name"] + "\nТы -- " + data["target"] + "\nТы -- " + data["gender"] +"\nТы находишься: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", data["latitude"], data["longitude"])).split(',')[-4:-1]))
