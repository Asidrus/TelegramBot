import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
import json
import logging
import io

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

counter = 0


class TelegramBot(Bot):
    db = None

    #для отправки сообщения 1 пользователю
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
 
    #перебор id пользователей
    async def broadcaster(self, msg, debug=None, id_sender=None) -> int:
        """
        Simple broadcaster

        :return: Count of messages
        """
        if id_sender is not None:
            # group = await self.db.get_attrForColumn(columns='group_id', table='users', param='id='+str(id_sender))
            # group = group[0]["group_id"]
            
            users_id = await self.db.get_attrForColumn(columns='id', table='users')
            # users_id = await self.db.get_attrForColumn(columns='id', table='users', param="group_id='"+group+"'")
            users_id = [rec["id"] for rec in users_id]
        else:
            if debug is None or debug==0:
                users_id = await self.db.fetch("SELECT users.id FROM users LEFT JOIN subscribes ON users.id=subscribes.uid where result_tests='1';")
                users_id = [rec["id"] for rec in users_id]
            elif debug==1:
                users_id = await self.db.fetch(f"SELECT users.id FROM users LEFT JOIN subscribes ON users.id=subscribes.uid where debug='true';")
                users_id = [rec["id"] for rec in users_id]
        try:
            for id in users_id:
                if await self._send_message(str(id), f'{msg}'):
                    # обнулить подписку пользователя
                    pass
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
        except Exception as e:
            raise e

    # Для изменения данных в таблицах subscribes и users
    async def groupTransfer(self, group, id, column=None):
        if column is not None:
            await self.db.updateData(column=column, table='subscribes', where='uid', param=1, id=id)
        
        await self.db.updateData(column='group_id', table='users', param=group, where='id', id=id)

    async def matchUser(self, group, uid, back_group=False):
        groupUser = await self.db.get_attrForColumn(columns = 'group_id', table='users', param=f'id={uid}')
        groupUser=groupUser[0]['group_id']
        res = False
        if len(group)>1:
            for item in group:
                if groupUser == item:
                    res = True
        else:
            if groupUser == group[0]:
                res = True
        if back_group:
            return [res, groupUser]
        else:
             return res

 
#################################### SERVER ################################################
   
    async def serve_client(self, reader, writer):
        global counter
        counter += 1  # Потоко-безопасно, так все выполняется в одном потоке
        print(f'Client connected')

        request = await self.read_request(reader)
        if request is None:
            print(f'Client  unexpectedly disconnected')
        else:
            await self.write_response(writer, request)
            print(request)

    async def read_request(self, reader):
        request = bytearray()
        while True:
            chunk = await reader.read(2 ** 10)
            # stream = io.BytesIO(screen)
            # img = Image.open(stream)
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


    async def write_response(self, writer, response):
        try:
            await self.broadcaster(msg=response['text'], debug=response['debug'])
            writer.write(b"{'status':'OK'}")
        except:
            writer.write(b"{'status':'ERROR'}")
        await writer.drain()
        writer.close()
        print(f'Client  has been served')

    async def run_server(self, host, port):
        server = await asyncio.start_server(self.serve_client, host, port)
        await server.serve_forever()


