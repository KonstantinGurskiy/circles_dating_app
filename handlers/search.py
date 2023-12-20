from aiogram import Router, F, Bot
from aiogram.types import Message, user, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
import asyncio
from utils.check_timer import check_timer
from keyboards.inline import name_btn, target_btn, look_for_btn, gender_btn, searching_start_btn, like_btn, check_profile_btn
from keyboards.builders import form_btn, form_loc_req
from keyboards.reply import main
from keyboards.builders import form_btn

from utils.search_machine import closest_person, write_likes, check_match
from utils.coord2loco import get_place
from data.database import DataBase
from time import sleep

router = Router()

@router.callback_query(lambda c: (c.data == 'search') | (c.data == 'like') | (c.data == 'dislike'))
async def check_user(callback: CallbackQuery, state: FSMContext, db: DataBase, bot: Bot):
    await bot.answer_callback_query(callback.id)
    df = await db.read_table()
    if(callback.message.chat.id in df['user_id'].values and check_timer(df[df['user_id'] == callback.message.chat.id]['time'].iat[0]) and df[df['user_id'] == callback.message.chat.id]['active'].iat[0]):
        await search_people(callback, state, db, bot)
    else:
        await callback.message.answer("Мы не нашли твоего аккаунта. Заполни нашу форму, пожалуйста:", reply_markup=main)


async def search_people(callback: CallbackQuery, state: FSMContext, db: DataBase, bot: Bot):
    # await clear_database(callback, state, db)
    await callback.message.answer("Ищу кандидата...")
    sleep(1)
    df = await db.read_table()
    if(callback.message.chat.id in df['user_id'].values):
        df = await db.read_table()

        if(callback.data == "like"):
            likes_to_write = await write_likes(df, callback.message.chat.id)
            await db.insert(likes_to_write[0])
            await db.insert(likes_to_write[1])
            ###добавим уведомления о лайках ждущим
            if(likes_to_write[1][5]==True):
                await bot.send_message(int(likes_to_write[0][0]), "Новое нравится❤! Посмотри:")
                await bot.send_video_note(int(likes_to_write[0][0]), likes_to_write[1][14])
                await bot.send_message(int(likes_to_write[0][0]), "Имя: " + likes_to_write[1][8] + "\nЦель: " + likes_to_write[1][11] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", likes_to_write[1][9], likes_to_write[1][10])).split(',')[-4:-1]), reply_markup=like_btn(["нравится ❤️", "следующий 👎"]))






        df = await db.read_table()
        matches, my_row = await check_match(df, callback.message.chat.id, db)
        if matches is not None:
            await db.insert(my_row)
            for match in matches:
                match = int(match)

                match_data = df[df['user_id'] == match].iloc[0].values.flatten().tolist()[1:]
                match_data[0] = str(match_data[0])
                match_data[5]=False
                match_data[6]=False
                await db.insert(match_data)


                username = df[df['user_id'] == match]['username'].iat[0]
                await callback.message.answer_video_note(df[df['user_id'] == match]['circle'].iat[0])
                await callback.message.answer(df[df['user_id'] == match]['name'].iat[0])
                await bot.send_location(callback.message.chat.id, df[df['user_id'] == match]['latitude'].iat[0], df[df['user_id'] == match]['longitude'].iat[0])
                await callback.message.answer(f"<a href='t.me/{username}'>It's a match!</a>", parse_mode=ParseMode.HTML)



                await bot.send_message(match, df[df['user_id'] == callback.message.chat.id]['name'].iat[0])
                await bot.send_video_note(match ,df[df['user_id'] == callback.message.chat.id]['circle'].iat[0])
                await bot.send_location(match, df[df['user_id'] == callback.message.chat.id]['latitude'].iat[0], df[df['user_id'] == callback.message.chat.id]['longitude'].iat[0])
                await bot.send_message(match, f"<a href='t.me/{df[df['user_id'] == callback.message.chat.id]['username'].iat[0]}'>It's a match!</a>", parse_mode=ParseMode.HTML)
        else:
            df = await db.read_table()
            contr_person = await closest_person(callback.message.chat.id, df)
            changed_row = df[df['user_id'] == callback.message.chat.id].iloc[0].values.flatten().tolist()[1:]
            if isinstance(contr_person, int):
                changed_row[0] = str(changed_row[0])
                changed_row[5] = str(1)
                changed_row[6] = str(changed_row[6])
                await db.insert(changed_row)
                await callback.message.answer("Пользователи кончились", reply_markup=check_profile_btn(["Изменить запрос", "Удалить запрос"]))
            else:
                changed_opponent_row = df[df['user_id'] == int(contr_person['user_id'])].iloc[0].values.flatten().tolist()[1:]
                await callback.message.answer_video_note(
                contr_person["circle"],
                )
                await callback.message.answer("Имя: " + contr_person["name"] + "\nЦель: " + contr_person["target"] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", contr_person["latitude"], contr_person["longitude"])).split(',')[-4:-1]), reply_markup=like_btn(["нравится ❤️", "следующий 👎"]))
                if changed_row[3]==None:
                    changed_row[3] = str(contr_person['user_id'])
                else:
                    changed_row[3] = str(changed_row[3])+ ' ' + str(contr_person['user_id'])

                changed_row[0] = str(changed_row[0])
                changed_row[5] = str(changed_row[5])
                changed_row[6] = str(changed_row[6])
                await db.insert(changed_row)



                if changed_opponent_row[4]==None:
                    changed_opponent_row[4] = str(callback.message.chat.id)
                else:
                    changed_opponent_row[4] = str(changed_opponent_row[4])+ ' ' + str(callback.message.chat.id)

                changed_opponent_row[0] = str(changed_opponent_row[0])
                changed_opponent_row[5] = str(changed_opponent_row[5])
                changed_opponent_row[6] = str(changed_opponent_row[6])
                await db.insert(changed_opponent_row)



# async def clear_database(callback: CallbackQuery, state: FSMContext, db: DataBase):
#     print("...cleaning db...")
#     await asyncio.sleep(1)
#     df = await db.read_table()
#     my_users = df[df['time'].apply(lambda x: not check_timer(x))]
#     print(my_users)
#     if not my_users.empty:
#         for user_id in my_users['user_id']:
#             await db.delete_user(int(user_id))
#


@router.message(Command("complain"))
async def form_photo(message: Message, state: FSMContext, db: DataBase):
    df = await db.read_table()

    if df[df['user_id'] == message.from_user.id]['already_saw'].values[0]!=None:
        her_id = df[df['user_id'] == message.from_user.id]['already_saw'].values[0].split(' ')[-1]
        her_data = df[df['user_id'] == int(her_id)].values[0][1:]
        if her_data[3]==None:
            her_data[3] = str(message.from_user.id)
        else:
            her_data[3] += ' ' + str(message.from_user.id)
        her_data[0]=str(her_data[0])
        her_data[5] = str(her_data[5])
        her_data[6] = str(her_data[6])
        await db.insert(her_data)
        await message.answer("Пользователь занесен в черный список\nПродолжить поиск?", reply_markup=searching_start_btn(["Изменить запрос", "Удалить запрос", "Продолжить поиск"]))
    else:
        await message.answer("Ты еще никого не посмотрел, а уже недоволен...", reply_markup=searching_start_btn(["Изменить запрос", "Удалить запрос", "Продолжить поиск"]))

