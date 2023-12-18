import aiosqlite
import pandas as pd
from utils.check_timer import check_timer

import geopy.distance
from data.database import DataBase
import asyncio

def subtract_lists(list1, list2):
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


    if target_value=="присоединиться к событию" and my_row['gender'].values[0]=="парень":
        my_users &= df['look_for'].isin(['всех!', 'парней'])
    elif target_value=="присоединиться к событию" and my_row['gender'].values[0]=="девушка":
        my_users &= df['look_for'].isin(['всех!', 'девушек'])
    elif target_value=="создать событие" and my_row['look_for'].values[0]=="парней":
        my_users &= df['gender'].isin(['парень'])
    elif target_value=="создать событие" and my_row['look_for'].values[0]=="девушек":
        my_users &= df['gender'].isin(['девушка'])



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
    if matches != []:
        likes = subtract_lists(likes, matches)
        liked = subtract_lists(liked, matches)
        my_data[1] = " ".join(map(str, likes))
        my_data[2] = " ".join(map(str, liked))
        if my_data[1] == "":
            my_data[1]=None
        if my_data[2] == "":
            my_data[2]=None
        my_data[5]=False
        return matches, my_data
    else:
        return None, None



