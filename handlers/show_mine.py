from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from data.database import DataBase
from utils.check_timer import check_timer
from keyboards.reply import main


from asyncio import sleep
from utils.coord2loco import get_place

router = Router()
db = DataBase("users_db.db", "users")

@router.message(Command("show"))
async def show_profile(message: Message, state: FSMContext, db: DataBase, bot: Bot):
    df = await db.read_table()
    if (df["user_id"].isin([message.from_user.id]).any() and  df[df['user_id']==message.from_user.id].iloc[0]['active'] == True):
        data = df[df['user_id']==message.from_user.id].iloc[0]
        if(check_timer(data['time'])):
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
    else:
        temp = [await message.answer("Мы не нашли твоего аккаунта. Заполни нашу форму, пожалуйста:", reply_markup=main)]
        # await insert_new_msgs_to_db(message.from_user.id, temp, await db.read_table(), db)
