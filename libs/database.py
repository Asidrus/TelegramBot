import asyncpg
from credentials import *


class DataBase:

    async def get_all_id(self):
        return await self.conn.fetch(f"Select id from users")

    async def run_db(self):
        self.conn = await asyncpg.connect(user=db_user,
                                          password=db_password,
                                          database=db_name,
                                          host=db_host)

    async def add_user(self, data):
        print(f"""INSERT into users (id, is_bot, first_name, last_name, language_code) 
            Values({data["id"]},{data["is_bot"]},{data["first_name"]},{data["last_name"]},{data["language_code"]})""")
        await self.conn.fetch(
            f"""INSERT into users (id, is_bot, first_name, last_name, language_code) 
            Values({data["id"]},{data["is_bot"]},'{data["first_name"]}','{data["last_name"]}','{data["language_code"]}')"""
        )

    async def get_user(self, id):
        if type(id) == int:
            return await self.conn.fetch(f"Select * from users where id = {id}")
        elif type(id) == tuple:
            return await self.conn.fetch(f"Select * from users where id in {id}")

    async def close(self):
        await self.conn.close()
