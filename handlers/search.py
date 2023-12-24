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

from utils.search_machine import closest_person, write_likes, check_match, notify_about_match
from utils.coord2loco import get_place
from data.database import DataBase
from asyncio import sleep
from utils.clean_chat import insert_new_msgs_to_db, delete_msgs


router = Router()

@router.callback_query(lambda c: (c.data == 'search') | (c.data == 'like') | (c.data == 'dislike'))
async def check_user(callback: CallbackQuery, state: FSMContext, db: DataBase, bot: Bot):
    await bot.answer_callback_query(callback.id)
    df = await db.read_table()
    if(callback.message.chat.id in df['user_id'].values and check_timer(df[df['user_id'] == callback.message.chat.id]['time'].iat[0]) and df[df['user_id'] == callback.message.chat.id]['active'].iat[0]):
        await search_people(callback, state, db, bot)
    else:
        temp = [await callback.message.answer("Мы не нашли твоего аккаунта. Заполни нашу форму, пожалуйста:", reply_markup=main)]
        await insert_new_msgs_to_db(callback.message.chat.id, temp, await db.read_table(), db)

async def search_people(callback: CallbackQuery, state: FSMContext, db: DataBase, bot: Bot):
    # await clear_database(callback, state, db)
    await delete_msgs(callback.message.chat.id, await db.read_table(), bot, db)
    temp = [await callback.message.answer("Ищу кандидата...")]
    await insert_new_msgs_to_db(callback.message.chat.id, temp, await db.read_table(), db)
    await bot.send_chat_action(callback.message.chat.id, action="typing")
    await sleep(1)
    df = await db.read_table()
    matches, my_row = await check_match(df, callback.message.chat.id, db)
    if matches is not None:
        await notify_about_match(matches, df, callback, state, db, bot)
    else:
        df = await db.read_table()

        if(callback.data == "like"):
            likes_to_write = await write_likes(df, callback.message.chat.id)
            await db.insert(likes_to_write[0])
            await db.insert(likes_to_write[1])

            ###добавим уведомления о лайках ждущим
            if(likes_to_write[1][5]==True):
                if likes_to_write[1][3]==None:
                    likes_to_write[1][3] = str(likes_to_write[0][0])
                else:
                    likes_to_write[1][3] = str(likes_to_write[1][3])+ ' ' + str(likes_to_write[0][0])
                await db.insert(likes_to_write[0])
                likes_to_write[1][5]=False
                await db.insert(likes_to_write[1])
                temp=[]
                temp.append(await bot.send_message(int(likes_to_write[1][0]), "Новое нравится❤! Посмотри:"))
                temp.append(await bot.send_video_note(int(likes_to_write[1][0]), likes_to_write[0][14]))
                temp.append(await bot.send_message(int(likes_to_write[1][0]), "Имя: " + likes_to_write[0][8] + "\nЦель: " + likes_to_write[0][11] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", likes_to_write[0][9], likes_to_write[0][10])).split(',')[-4:-1]), reply_markup=like_btn(["нравится ❤️", "следующий 👎"])))
                print("Я отправил лайк")
                await insert_new_msgs_to_db(int(likes_to_write[1][0]), temp, await db.read_table(), db)

            df = await db.read_table()
            matches, my_row = await check_match(df, callback.message.chat.id, db)
            if matches != None:
                print("notify")
                await notify_about_match(matches, df, callback, state, db, bot)



        else:
            df = await db.read_table()
            contr_person = await closest_person(callback.message.chat.id, df)
            changed_row = df[df['user_id'] == callback.message.chat.id].iloc[0].values.flatten().tolist()[1:]
            if isinstance(contr_person, int):
                changed_row[0] = str(changed_row[0])
                changed_row[5] = str(1)
                changed_row[6] = str(changed_row[6])
                await db.insert(changed_row)
                temp = [await callback.message.answer("Пользователи кончились")]
                await insert_new_msgs_to_db(callback.message.chat.id, temp, await db.read_table(), db)
            else:
                changed_opponent_row = df[df['user_id'] == int(contr_person['user_id'])].iloc[0].values.flatten().tolist()[1:]
                temp = []
                temp.append(await callback.message.answer_video_note(contr_person["circle"]))
                temp.append(await callback.message.answer("Имя: " + contr_person["name"] + "\nЦель: " + contr_person["target"] + "\nОткуда: " + ','.join(str(await get_place("073e8a55524f48048a75d1ba0dc83bd6", contr_person["latitude"], contr_person["longitude"])).split(',')[-4:-1]), reply_markup=like_btn(["нравится ❤️", "следующий 👎"])))
                await insert_new_msgs_to_db(callback.message.chat.id, temp, await db.read_table(), db)
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
        temp = [await message.answer("Пользователь занесен в черный список\nПродолжить поиск?", reply_markup=searching_start_btn(["Продолжить поиск"]))]
        await insert_new_msgs_to_db(message.from_user.id, temp, await db.read_table(), db)
    else:
        temp = [await message.answer("Ты еще никого не посмотрел, а уже недоволен...", reply_markup=searching_start_btn(["Продолжить поиск"]))]
        await insert_new_msgs_to_db(message.from_user.id, temp, await db.read_table(), db)
