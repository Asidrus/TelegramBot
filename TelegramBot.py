import asyncio
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

counter = 0

users = []


def get_users():
    yield from users


def read_users():
    with open("ids", "r") as r:
        data = r.readlines()
    data = [d[:-1] for d in data]
    return data


def write_users(user_id):
    with open("ids", "a") as w:
        w.writelines(user_id + "\n")


class TelegramBot(Bot):

    async def _send_message(self, user_id: int, text: str, disable_notification: bool = False) -> bool:
        """
        Safe messages sender

        :param user_id:
        :param text:
        :param disable_notification:
        :return:
        """
        try:
            await self.send_message(user_id, text, disable_notification=disable_notification)
        except exceptions.BotBlocked:
            log.error(f"Target [ID:{user_id}]: blocked by user")
        except exceptions.ChatNotFound:
            log.error(f"Target [ID:{user_id}]: invalid user ID")
        except exceptions.RetryAfter as e:
            log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
            await asyncio.sleep(e.timeout)
            return await self._send_message(user_id, text)  # Recursive call
        except exceptions.UserDeactivated:
            log.error(f"Target [ID:{user_id}]: user is deactivated")
        except exceptions.TelegramAPIError:
            log.exception(f"Target [ID:{user_id}]: failed")
        else:
            log.info(f"Target [ID:{user_id}]: success")
            return True
        return False

    async def broadcaster(self, msg) -> int:
        """
        Simple broadcaster

        :return: Count of messages
        """
        count = 0
        try:
            for user_id in get_users():
                if await self._send_message(user_id, f'{msg}'):
                    count += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
        finally:
            log.info(f"{count} messages successful sent.")
        return count

    async def serve_client(self, reader, writer):
        global counter
        cid = counter
        counter += 1  # Потоко-безопасно, так все выполняется в одном потоке
        print(f'Client #{cid} connected')

        request = await self.read_request(reader)
        if request is None:
            print(f'Client #{cid} unexpectedly disconnected')
        else:
            response = await self.handle_request(request)
            await self.write_response(writer, response, cid)

    async def handle_request(self, request):
        await asyncio.sleep(5)
        return request[::-1]

    async def read_request(self, reader, delimiter=b'!'):
        request = bytearray()
        while True:
            chunk = await reader.read(4)
            if not chunk:
                # Клиент преждевременно отключился.
                break
            request += chunk
            if delimiter in request:
                return request
        return None

    async def write_response(self, writer, response, cid):
        await self.broadcaster(response.decode())
        print(response)
        writer.write(response)
        await writer.drain()
        writer.close()
        print(f'Client #{cid} has been served')

    async def run_server(self, host, port):
        server = await asyncio.start_server(self.serve_client, host, port)
        await server.serve_forever()

users = read_users()


class db:

    user = ""
    password = ""
    database = ""
    host = ""

    async def run_db(self):
        self.conn = await asyncpg.connect(user=self.user,
                                     password=self.password,
                                     database=self.database,
                                     host=self.host)

    # async def get(self, request):
    #     values = await self.conn.fetch("SELECT * FROM mytable WHERE id = $1")

    async def add_user(self, data):
        await self.conn.fetch(
            f"""INSERT into users (id, is_bot, first_name, last_name, language_code) 
            Values({data["id"]},{data["is_bot"]},{data["first_name"]},{data["last_name"]},{data["language_code"]})"""
        )

    async def get_user(self, ids: list):
        return await self.conn.fetch(f"Select * from users where id in {ids}")

    async def close(self):
        await self.conn.close()