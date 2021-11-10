import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
import json

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

counter = 0


class TelegramBot(Bot):
    db = None

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

    async def broadcaster(self, msg, debug=None, id_sender=None) -> int:
        """
        Simple broadcaster

        :return: Count of messages
        """
        if id_sender is not None:
            group = await self.db.get_attrForColummn(columns='group_id', table='users', param='uid='+str(id_sender))
            group = group[0]["group_id"]
            users_id = await self.db.get_attrForColummn(columns='uid', table='users', param="group_id='"+group+"'")
            users_id = [rec["uid"] for rec in users_id]
        else:
            if debug is None:
                users_id = await self.db.fetch("SELECT users.uid FROM users LEFT JOIN subscrib ON users.id=subscrib.uid where result_tests='1';")
                users_id = [rec["uid"] for rec in users_id]
            else:
                users_id = await self.db.fetch(f"SELECT users.uid FROM users LEFT JOIN subscrib ON users.id=subscrib.uid where debug='"+ 1 if debug=='True' else 0 +"';")
                users_id = [rec["uid"] for rec in users_id]
        try:
            for id in users_id:
                if await self._send_message(str(id), f'{msg}'):
                    # обнулить подписку пользователя
                    pass
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
        except Exception as e:
            raise e


    async def serve_client(self, reader, writer):
        global counter
        cid = counter
        counter += 1  # Потоко-безопасно, так все выполняется в одном потоке
        print(f'Client #{cid} connected')

        request = await self.read_request(reader)
        if request is None:
            print(f'Client #{cid} unexpectedly disconnected')
        else:
            # await self.write_response(writer, request, cid)
            print(request)

    async def read_request(reader, delimiter=b'#END'):
        request = bytearray()
        while True:
            chunk = await reader.read(2 ** 10)
            if not chunk:
                # Клиент преждевременно отключился.
                break
            request += chunk
            try:
                data = json.loads(request.decode("utf-8").replace("'", "\""))
                return data
            except:
                pass
            # if delimiter in request:
            #     return request[:-2]
        return None

    async def write_response(self, writer, response, cid):
        # await self.broadcaster(response.decode())
        writer.write(response)
        await writer.drain()
        writer.close()
        print(f'Client #{cid} has been served')

    async def run_server(self, host, port):
        server = await asyncio.start_server(self.serve_client, host, port)
        print(server)
        await server.serve_forever()


