import aiosqlite


class DataBase:

    def __init__(self, name: str, table: str) -> None:
        self.name = name
        self.table = table

    async def create_table(self):
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()

            query = """
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(20),
                age INTEGER(2),
                sex INTEGER(1),
                city VARCHAR(255),
                look_for INTEGER(1),
                about TEXT(500),
                photo VARCHAR(255)
            )
            """

            await cursor.executescript(query)
            await db.commit()

    async def insert(self, **kwargs) -> None:
        async with aiosqlite.connect(self.name) as db:
            cursor = await db.cursor()
            await cursor.execute(
                """
                INSERT INTO users(
                    name,
                    age,
                    city,
                    sex,
                    look_for,
                    about
                ) VALUES(?, ?, ?, ?, ?, ?)
                """,
                **kwargs
            )
