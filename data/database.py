import aiosqlite
import pandas as pd

class DataBase:

    def __init__(self, name: str, table: str) -> None:
        self.name = f"data/{name}"
        self.table = table

    async def create_table(self) -> None:
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            query = """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER(10),
                likes TEXT(99999),
                liked TEXT(99999),
                already_saw TEXT(99999),
                already_seen_by TEXT(99999),
                waiting INTEGER(1),
                active INTEGER(1),
                time TEXT(20),
                name VARCHAR(20),
                latitude REAL(10),
                longitude REAL(10),
                target INTEGER(1),
                gender TEXT(10),
                look_for TEXT(10),
                circle VARCHAR(255),
                username VARCHAR(255),
                msgs_to_delete TEXT(99999)
            )
            """

            await cursor.executescript(query)
            await db.commit()

    async def insert(self, data) -> None:
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            # Проверяем, существует ли запись с user_id
            await cursor.execute("SELECT * FROM users WHERE user_id="+ str(data[0]))
            existing_record = await cursor.fetchone()
            if existing_record:
                # Если запись существует, обновляем её
                await cursor.execute("UPDATE users SET user_id=?, likes=?, liked=?, already_saw=?, already_seen_by=?, waiting=?, active=?, time=?, name=?, latitude=?, longitude=?, target=?, gender=?, look_for=?, circle=?, username=?, msgs_to_delete = ? WHERE user_id="+ str(data[0]), data)
            else:
                # Если запись не существует, вставляем новую запись
                await cursor.execute(
                """
                INSERT INTO users(
                    user_id,
                    likes,
                    liked,
                    already_saw,
                    already_seen_by,
                    waiting,
                    active,
                    time,
                    name,
                    latitude,
                    longitude,
                    target,
                    gender,
                    look_for,
                    circle,
                    username,
                    msgs_to_delete
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                data
            )

            await db.commit()

    async def delete_user(self, user_id) -> None:
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()

            # Удаляем пользователя по его ID
            await cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))

            await db.commit()





    async def read_table(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM users")
            rows = [list(row) for row in await cursor.fetchall()]
            column_names = ['id', 'user_id', 'likes', 'liked', 'already_saw', 'already_seen_by', 'waiting', 'active', 'time', 'name', 'latitude', 'longitude', 'target', 'gender', 'look_for', 'circle', 'username', 'msgs_to_delete']
            df = pd.DataFrame(rows, columns=column_names)
            return df
