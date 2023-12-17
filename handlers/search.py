from aiogram import Router, F
from aiogram.types import Message, user
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from keyboards.builders import form_btn

from utils.search_machine import closest_person, write_likes, check_match
from utils.coord2loco import get_place
from data.database import DataBase

router = Router()

@router.message(Command("search", "like", "dislike"))
async def search_people(message: Message, state: FSMContext, db: DataBase):
    df = await db.read_table()
    if(message.from_user.id in df['user_id'].values):
        df = await db.read_table()

        if(message.text == "/like"):
            likes_to_write = await write_likes(df, message.from_user.id)
            await db.insert(likes_to_write[0])
            await db.insert(likes_to_write[1])



        df = await db.read_table()
        matches, my_row = await check_match(df, message.from_user.id, db)
        if matches is not None:
            await db.insert(my_row)
            for match in matches:
                match = int(match)
                username = df[df['user_id'] == match]['username'].iat[0]
                await message.answer_video_note(df[df['user_id'] == match]['circle'].iat[0])
                await message.answer(df[df['user_id'] == match]['name'].iat[0], reply_markup=form_btn(["/like", "/dislike"]))
                await message.answer(f"<a href='t.me/{username}'>It's a match!</a>", parse_mode=ParseMode.HTML)


        df = await db.read_table()
        contr_person = await closest_person(message.from_user.id, df)
        changed_row = df[df['user_id'] == message.from_user.id].iloc[0].values.flatten().tolist()[1:]
        if isinstance(contr_person, int):
            await message.answer("Пользователи кончились", reply_markup=form_btn(["/create", "/search"]))
        else:
            await message.answer_video_note(
            contr_person["circle"],
            )
            await message.answer("Имя: " + contr_person["name"] + "\nЦель: " + contr_person["target"] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", contr_person["latitude"], contr_person["longitude"])).split(',')[-4:-1]), reply_markup=form_btn(["/like", "/dislike"]))
            if changed_row[3]==None:
                changed_row[3] = str(contr_person['user_id'])
            else:
                changed_row[3] = str(changed_row[3])+ ' ' + str(contr_person['user_id'])
            changed_row[0] = str(changed_row[0])
            changed_row[5] = str(changed_row[5])
            await db.insert(changed_row)
    else:
        await message.answer("Мы не нашли твоего аккаунта. Заполни нашу форму, пожалуйста:", reply_markup=form_btn(["/create"]))
