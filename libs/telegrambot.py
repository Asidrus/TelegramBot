import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
import json
import logging
import io
import uuid
import hashlib

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')

counter = 0


class TelegramBot(Bot):
    db = None

    # для отправки сообщения 1 пользователю
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

    # перебор id пользователей
    async def broadcaster(self, contentType='text', content='', debug=0, id_sender=None, image=None) -> int:
        text = content["msg"]
        if 'rt_penta' in content.keys():
            penta = content['rt_penta']
        elif 'rt_MD' in content.keys():
            Mult = content['rt_penta']
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
            if debug == 0:
                users_id = await self.db.fetch(
                    "SELECT users.id FROM users LEFT JOIN subscribes ON users.id=subscribes.uid where result_tests='true';")
                users_id = [rec["id"] for rec in users_id]
            elif debug == 1:
                users_id = await self.db.fetch(
                    f"SELECT users.id FROM users LEFT JOIN subscribes ON users.id=subscribes.uid where debug='true';")
                users_id = [rec["id"] for rec in users_id]

        try:
            for id in users_id:
                if await self._send_message(str(id), f'{content}'):
                    # обнулить подписку пользователя
                    pass
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)

                if image is not None and len(image) != 0:
                    await self.send_photo(chat_id=id, photo=image)
                    await asyncio.sleep(.05)
        except Exception as e:
            raise e

    # Для изменения данных в таблицах subscribes и users
    async def groupTransfer(self, group, id, column=None):
        if column is not None:
            await self.db.updateData(column=column, table='subscribes', where='uid', param=1, id=id)

        await self.db.updateData(column='group_id', table='users', param=group, where='id', id=id)

    async def matchUser(self, group, uid, back_group=False):
        groupUser = await self.db.get_attrForColumn(columns='group_id', table='users', param=f'id={uid}')
        groupUser = groupUser[0]['group_id']
        res = False
        if len(group) > 1:
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

    async def check_password(self, hashed_password, user_password):
        password, salt = hashed_password.split(':')
        return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()
 
    async def subscriptionAnalysis(self, userId):
        subscr = await self.db.get_attrForColumn(columns='res_all_tests, rt_penta, rt_psy, rt_mult', table='subscribes', param=f'uid={userId}')
        subscr = [dict(row) for row in subscr]
        if subscr[0]['rt_penta']==False and subscr[0]['rt_psy']==False and subscr[0]['rt_mult']==False:
            return False
        else:
            return True
    
    async def checkingSubscriptions(self, group, id, purpose=None):
        subscrname = []  
        subscribes = ''
        subs = await self.db.get_attrForColumn(columns='*', table='subscribes',
                                                 param=f'uid={id}')
        subs = [dict(row) for row in subs]
        print(subs)
        if purpose is None:
            if group == '0':
                if not subs[0]['debug']:
                    subscrname.append('debug')
            
            if not subs[0]['from_users']:
                subscrname.append('from_users')
            if not subs[0]['res_all_tests']:
                subscrname.append('res_all_tests')
            if not subs[0]['rt_penta'] :
                subscrname.append('rt_penta')
            if not subs[0]['rt_psy']:
                subscrname.append('rt_psy')
            if not subs[0]['rt_mult']:
                subscrname.append('rt_mult')
            return subscrname
        else:
            if group == '0':
                if subs[0]['debug']:
                    subscribes = ' "Дебаг" '
            if subs[0]['from_users']:
                subscribes = subscribes + ' "Общие" '
            if subs[0]['res_all_tests']:
                subscribes = subscribes + ' "Все тесты" '
            if subs[0]['rt_penta']:
                subscribes = subscribes + ' "УЦ - "Pentaschool" " '   
            if subs[0]['rt_psy']:
                subscribes = subscribes + ' УЦ - "PSY" '
            if subs[0]['rt_mult']:
                subscribes = subscribes + ' УЦ - "Мультидвижок" '
            return subscribes