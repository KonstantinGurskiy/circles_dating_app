import aiosqlite
import pandas as pd

import geopy.distance
from data.database import DataBase


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
        # print(min_idx)
        # print(my_users.values[min_idx])
        return my_users.iloc[min_idx]

async def write_likes(df, my_id: int, her_id: int):
    my_data = df[df['user_id'] == my_id].values[0][1:]
    her_data = df[df['user_id'] == her_id].values[0][1:]
    my_data[0] = str(my_data[0])
    her_data[0] = str(her_data[0])
    my_data[1] += ', ' + str(her_id)
    her_data[2] += ', ' + str(my_id)
    return [list(my_data), list(her_data)]


async def check_match(my_id: int):
    ...
