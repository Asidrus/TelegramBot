import asyncpg
import os

from dotenv import load_dotenv
load_dotenv()

ENV_LOCAL = '.env_local'
if os.path.isfile(ENV_LOCAL):
    load_dotenv(ENV_LOCAL)

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

cred = {"user": DB_USER,
        "password": DB_PASSWORD,
        "database": DB_NAME,
        "host": DB_HOST}

def db_connection(**kwargs):
    """
    @db_connection(user="...", password="...", database="...", host="...")
    getData(connection):
        await = connection.fetch("SELECT * FROM ...")
    """

    def _wrapper(func):
        async def wrapper(*args, **params):
            connection = await asyncpg.connect(**kwargs)
            params["connection"] = connection
            result = await func(*args, **params)
            await connection.close()
            return result

        return wrapper

    return _wrapper

class DataBase:

    @db_connection(**cred)
    async def get_all_id(self, connection):
        return await connection.fetch(f"Select id from users")

    @db_connection(**cred)
    async def add_user(self, data, connection):
        await connection.fetch(
              f"""CALL public.add_user({data["id"]},'{data["is_bot"]}','{data["first_name"]}', '{data["last_name"]}', '{data["language_code"]}')"""
        )


    @db_connection(**cred)
    async def get_user(self, id, connection):
        if type(id) == int:
            return await connection.fetch(f"Select * from users where id = {id}")
        elif type(id) == tuple:
            return await connection.fetch(f"Select * from users where id in {id}")


    @db_connection(**cred)
    async def get_attrForColumn(sels, columns: str, table: str, connection, param=None):
        if param is None:
            return await connection.fetch(f"Select {columns} from {table}")
        else:
            # print(f"Select {columns} from {table} where {param}")
            return await connection.fetch(f"Select {columns} from {table} where {param}")

    @db_connection(**cred)
    async def updateData(sels, column, table, param, where, id, connection):
        return await connection.fetch(f"UPDATE {table} SET {column}='{param}' where {where}={id}")


    @db_connection(**cred)
    async def fetch(self, request: str, connection):
        return await connection.fetch(request)