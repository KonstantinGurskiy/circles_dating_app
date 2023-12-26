from data.database import DataBase
from utils.check_timer import check_timer

async def how_much(db):
    df = await db.read_table()
    # Подсчет строк, где значения в столбцах 'waiting' и 'active' не равны нулю
    filtered_rows = df[(df['waiting'] != False) & (df['active'] != False) & (df['time'].apply(lambda x: check_timer(x)))]

    return str(len(filtered_rows))
