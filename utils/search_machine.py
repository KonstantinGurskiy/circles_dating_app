import aiosqlite
import pandas as pd

import geopy.distance
from data.database import DataBase

def subtract_lists(list1, list2):
    for item in list2:
        while item in list1:
            list1.remove(item)
    return list1

def list_to_string_with_prefix(my_list, prefix=" "):
    result_string = prefix + ", ".join(map(str, my_list))
    return result_string



async def closest_person(my_id: int, df):
    target_value = str(df[df['user_id'] == my_id]['target'].values[0])
    seen = [int(element) for element in df.loc[df['user_id'] == my_id, 'already_seen'].values[0].split(', ')[1:]]
    my_users = df[(df['user_id'] != my_id) & (df['target'] != target_value) & (~df['user_id'].isin(seen))]
    # Вычисляем расстояния
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

async def write_likes(df, my_id: int, her_id: int):
    my_data = df[df['user_id'] == my_id].values[0][1:]
    her_data = df[df['user_id'] == her_id].values[0][1:]
    my_data[0] = str(my_data[0])
    her_data[0] = str(her_data[0])
    my_data[1] += ', ' + str(her_id)
    her_data[2] += ', ' + str(my_id)
    return [list(my_data), list(her_data)]


async def check_match(df, my_id: int, db):
    my_data = df[df['user_id'] == my_id].values[0][1:]
    my_data[0] = str(my_data[0])
    likes = my_data[1].split(', ')[1:]
    liked = my_data[2].split(', ')[1:]
    matches = 0
    matches = list(set(likes) & set(liked))
    if matches != 0:
        likes = subtract_lists(likes, matches)
        liked = subtract_lists(liked, matches)
        my_data[1] = list_to_string_with_prefix(likes)
        my_data[2] = list_to_string_with_prefix(liked)

    return matches, my_data



