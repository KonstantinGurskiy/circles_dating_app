import asyncio
from contextlib import suppress
from data.database import DataBase
from aiogram import types
from aiogram import Bot

async def delete_msgs(my_id, df, bot, db, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    my_row = df[df['user_id'] == my_id].iloc[0].values.flatten().tolist()[1:]
    msgs = my_row[-1]
    msgs = msgs.split(' ')
    print(msgs)
    for msg in msgs:
        print(int(msg))
        try:
            await bot.delete_message(my_id, int(msg))
        except:
            print("Я не нашел сообщение")
    await db.insert(await clean_msgs(my_id, df))
    print("Удалил сообщения")


async def insert_new_msgs_to_db(my_id, msgs: int | list, df, db):
    my_row = df[df['user_id'] == my_id].iloc[0].values.flatten().tolist()[1:]

    my_msgs = my_row[-1]
    for msg in msgs:
        # print(msg.message_id)
        if my_msgs==None:
            my_msgs=str(msg.message_id)
        else:
            my_msgs += ' ' + str(msg.message_id)
    my_row[0] = str(my_row[0])
    my_row[5] = str(my_row[5])
    my_row[6] = str(my_row[6])
    my_row[-1] = my_msgs
    print("Записал сообщения на удаление")
    await db.insert(my_row)


async def clean_msgs(my_id, df):
    my_row = df[df['user_id'] == my_id].iloc[0].values.flatten().tolist()[1:]
    my_row[0] = str(my_row[0])
    my_row[5] = str(my_row[5])
    my_row[6] = str(my_row[6])
    my_row[-1] = None
    return my_row
