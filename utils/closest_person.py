import aiosqlite
import pandas as pd

from scipy.spatial.distance import cdist
from data.database import DataBase

async def search_machine(my_id: int):
    db = DataBase("users_db.db", "users")
    df = await db.read_table()
    print(df)
    # Отфильтровываем по my_id и цели
    my_data = df[(df['user_id'] != my_id) & (df['target'] != df[df['user_id'] == my_id]['target'].iloc[0])]

    # Вычисляем расстояния
    distances = cdist(my_data[['latitude', 'longitude']], df[df['user_id'] == my_id][['latitude', 'longitude']])

    # Находим ближайшего пользователя
    closest_user_id = my_data.iloc[distances.argmin()]['user_id']

    print(f"The closest user_id to my_id={my_id} is {closest_user_id}")
