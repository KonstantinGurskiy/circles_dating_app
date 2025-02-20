import aiosqlite
import pandas as pd
from utils.check_timer import check_timer

import geopy.distance
from data.database import DataBase
import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message, user, CallbackQuery
from asyncio import sleep
from aiogram.enums import ParseMode
from utils.clean_chat import delete_msgs

async def subtract_lists(list1, list2):
    for item in list2:
        while item in list1:
            list1.remove(item)
    # if list1==[]:
        # return None
    return list1



async def closest_person(my_id: int, df):
    my_row = df[df['user_id'] == my_id]
    target_value = str(my_row['target'].values[0])

    if my_row['already_saw'].values[0]!=None:
        seen = [int(element) for element in my_row['already_saw'].values[0].split(' ')]
    else:
        seen=[]

    my_users = df[(df['user_id'] != my_id) & (df['target'] != target_value) & (~df['user_id'].isin(seen)) & (df['active']==True) & (df['time'].apply(lambda x: check_timer(x)))]


    if target_value=="гость события" and my_row['gender'].values[0]=="парень":
        my_users = my_users[my_users['look_for'].isin(['всех!', 'парней'])]
    elif target_value=="гость события" and my_row['gender'].values[0]=="девушка":
        my_users = my_users[my_users['look_for'].isin(['всех!', 'девушек'])]
    elif target_value=="создатель события" and my_row['look_for'].values[0]=="парней":
        my_users = my_users[my_users['gender'].isin(['парень'])]
    elif target_value=="создатель события" and my_row['look_for'].values[0]=="девушек":
        my_users = my_users[my_users['gender'].isin(['девушка'])]


    if target_value == 'создатель события':
        if my_row['liked'].values[0]!=None:
            liked = [int(x) for x in my_row['liked'].values[0].split(' ')]
            my_users = my_users[df['user_id'].isin(liked)]
        else:
            my_users = pd.DataFrame([])

    coords1 = (df.loc[df['user_id'] == my_id, 'latitude'].values[0], df.loc[df['user_id'] == my_id, 'longitude'].values[0])
    min_distance = 99999
    min_idx = -1
    for i in range(len(my_users)):
        coords2 = (my_users['latitude'].values[i], my_users['longitude'].values[i])
        distance = geopy.distance.geodesic(coords1, coords2).km
        if distance < min_distance:
            min_distance = distance
            min_idx = i
    if min_idx==-1:
        return min_idx
    else:
        return my_users.iloc[min_idx]

async def write_likes(df, my_id: int):
    her_id = df[df['user_id'] == my_id]['already_saw'].values[0].split(' ')[-1]
    my_data = df[df['user_id'] == my_id].values[0][1:]
    her_data = df[df['user_id'] == int(her_id)].values[0][1:]
    my_data[0] = str(my_data[0])
    her_data[0] = str(her_data[0])
    if my_data[1]==None:
        my_data[1] = str(her_id)
    else:
        my_data[1] += ' ' + str(her_id)

    if her_data[2]==None:
        her_data[2] = str(my_id)
    else:
        her_data[2] += ' ' + str(my_id)
    return [list(my_data), list(her_data)]


async def check_match(df, my_id: int, db):
    my_data = df[df['user_id'] == my_id].values[0][1:]
    print(my_data)
    my_data[0] = str(my_data[0])
    if my_data[1]!=None:
        likes = my_data[1].split(' ')
    else:
        return None, None


    if my_data[2]!=None:
        liked = my_data[1].split(' ')
    else:
        return None, None

    matches = list(set(likes) & set(liked))
    print(likes)
    print(liked)
    print(matches)
    if matches != []:
        likes = await subtract_lists(likes, matches)
        liked = await subtract_lists(liked, matches)
        my_data[1] = " ".join(map(str, likes))
        my_data[2] = " ".join(map(str, liked))
        if my_data[1] == "":
            my_data[1]=None
        if my_data[2] == "":
            my_data[2]=None
        my_data[5]=False
        my_data[6]=False
        return matches, my_data
    else:
        return None, None


async def notify_about_match(matches, df, clb, st, db, bot):
    await delete_msgs(clb.message.chat.id, await db.read_table(), bot, db)
    for match in matches:
        match = int(match)
        await delete_msgs(match, await db.read_table(), bot, db)
        print("Сообщаю пользователю о мэтче")
        match_data = df[df['user_id'] == match].iloc[0].values.flatten().tolist()[1:]
        match_data[0] = str(match_data[0])
        match_data[5]=False
        match_data[6]=False
        await db.insert(match_data)


        my_id = int(clb.message.chat.id)
        print("Сообщаю пользователю о мэтче")
        my_row = df[df['user_id'] == my_id].iloc[0].values.flatten().tolist()[1:]
        my_row[0] = str(my_row[0])
        my_row[5]=False
        my_row[6]=False
        await db.insert(my_row)



        username = df[df['user_id'] == match]['username'].iat[0]
        await clb.message.answer("Соединяю...")
        await bot.send_chat_action(clb.message.chat.id, action="typing")
        await sleep(1)
        await clb.message.answer_video_note(df[df['user_id'] == match]['circle'].iat[0])
        await clb.message.answer(df[df['user_id'] == match]['name'].iat[0] + "\nРасстояние до тебя: " + str(round(geopy.distance.geodesic((my_row[10], my_row[11]), (match[10], match[11])).km, 1)) + " км")
        # await bot.send_location(clb.message.chat.id, df[df['user_id'] == match]['latitude'].iat[0], df[df['user_id'] == match]['longitude'].iat[0])
        await clb.message.answer(f"<a href='t.me/{username}'>It's a match!</a>", parse_mode=ParseMode.HTML)


        await bot.send_message(match, "Соединяю...")
        await bot.send_chat_action(clb.message.chat.id, action="typing")
        await sleep(1)
        await bot.send_message(match, df[df['user_id'] == clb.message.chat.id]['name'].iat[0] + "\nРасстояние до тебя: " + str(round(geopy.distance.geodesic((my_row[10], my_row[11]), (match[10], match[11])).km, 1)) + " км")
        await bot.send_video_note(match ,df[df['user_id'] == clb.message.chat.id]['circle'].iat[0])
        # await bot.send_location(match, df[df['user_id'] == clb.message.chat.id]['latitude'].iat[0], df[df['user_id'] == clb.message.chat.id]['longitude'].iat[0])
        await bot.send_message(match, f"<a href='t.me/{df[df['user_id'] == clb.message.chat.id]['username'].iat[0]}'>It's a match!</a>", parse_mode=ParseMode.HTML)
