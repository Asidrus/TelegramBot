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
    subscribes = {'All': 'from_users', 'All tests': 'res_all_tests', 'Osek': 'rt_spo', 'Pentaschool': 'rt_penta', 'Psy': 'rt_psy', 'Mult': 'rt_mult', 'debug': 'debug'}

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
    async def broadcaster(self, contentType='text', content=None, id_sender=None, image=None, project=None, id_media=None) -> int:
        if contentType == 'text':
            pass
        elif contentType == 'json':
            if (content is not None) and (content['project'] is not None):
                project = content['project']
            content = content['msg']

        """
        Simple broadcaster
        :return: Count of messages
        """

        print(project)

        if project == 'all':
            users_id = await self.db.get_attrForColumn(columns='id', table='users', param="group_id!='3'")

            users_id = [rec["id"] for rec in users_id]

        elif project == 'mult' or project == "penta" or project == "psy" or project == "spo":
            if id_sender is not None:
                users_id = await self.db.get_attrForColumn(columns='uid', table='subscribes', param=f"rt_{project}='true' OR uid='{id_sender}' or res_all_tests='true'")
            else:
                users_id = await self.db.get_attrForColumn(columns='uid', table='subscribes', param=f"rt_{project}='true' or res_all_tests='true'")
                
            users_id = [rec["uid"] for rec in users_id]

           
        elif project == 'debug' or project == "":
            users_id = await self.db.fetch(
                    f"SELECT users.id FROM users LEFT JOIN subscribes ON users.id=subscribes.uid where debug='true';")
            users_id = [rec["id"] for rec in users_id]

        if  len(users_id) == 1 and len(users_id) == 0 and id_sender==None:
            await self._send_message(str(id_sender), 'Пользователи не найдены')
        else: 
            try:
        
                for id in users_id:
                    if await self._send_message(str(id), f'{content}'):
                        # обнулить подписку пользователя
                        pass
                    await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)

                    if image is not None and len(image) != 0:
                        await self.send_photo(chat_id=id, photo=image)
                        await asyncio.sleep(.05)

                    if  id_media is not None:
                        if 'video' in id_media.keys():
                            await self.send_animation(chat_id=id, animation=id_media['video'])
                            await asyncio.sleep(.05)
                        elif 'photo' in id_media.keys():
                            await self.send_photo(chat_id=id, photo=id_media['photo'])
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

    async def checkingSubscriptions(self, id, group=None, purpose=None):
        subscribes = ''
        subs = await self.db.get_attrForColumn(columns='debug, from_users as "All", res_all_tests as "All tests", rt_penta as "Pentaschool", rt_psy as "Psy", rt_mult as "Mult", rt_spo as "Osek"', table='subscribes',
                                                 param=f'uid={id}')
        subs = [dict(row) for row in subs]
        if group!='0':
                del subs[0]['debug']
        if purpose=='subs':
            return subs[0]
        elif purpose=='my_subs':
            for key, val in subs[0].items():
                if val:
                    subscribes = subscribes + f' "{key}" '
            return subscribes
        elif purpose=='УЦ':
            if (subs[0]['Pentaschool']==False) and (subs[0]['Psy']==False) and (subs[0]['Mult']==False) and (subs[0]['Osek']==False):
                return False
            else:
                return True
    
    async def workSubscribes(self, uid, act, flag=None):
        try:
            if flag is None:
                await self.db.updateData(column=f'{self.subscribes[act]}', param='1', table = 'subscribes', where='uid', id=uid)
            else:
                await self.db.updateData(column=f'{self.subscribes[act]}', param='0', table = 'subscribes', where='uid', id=uid)

            return True
        except Exception as e:
            print(e)
            return False