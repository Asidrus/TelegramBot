import asyncio
import logging
from threading import Thread

from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor

counter = 0


class ServerBot(Bot):

    def run(self, host, port):
        asyncio.run(self.run_server(host, port))

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

    async def handle_request(self, request):
        await asyncio.sleep(5)
        return request[::-1]

    async def write_response(self, writer, response, cid):
        await self.broadcaster(response)
        writer.write(response)
        await writer.drain()
        writer.close()
        print(f'Client #{cid} has been served')

    async def run_server(self, host, port):
        server = await asyncio.start_server(self.serve_client, host, port)
        await server.serve_forever()

    def get_users(self):
        """
        Return users list

        In this example returns some random ID's
        """
        yield from (936364717,)

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
            for user_id in self.get_users():
                if await self._send_message(user_id, f'<a>{msg.decode()}!</a>'):
                    count += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
        finally:
            log.info(f"{count} messages successful sent.")
        return count

API_TOKEN = "1924016224:AAF4TufT_s-WLu5a1WbXOl04NL9Wfq0MpEI"
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')
bot = ServerBot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
bot.run("localhost", 1234)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    await msg.reply_to_message(f"Я бот. Приятно познакомиться,{msg.from_user.first_name}")


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
        print(msg.from_user.id)
        await msg.answer('Привет!')
    else:
        await msg.answer('Не понимаю, что это значит.')



executor.start_polling(dp)
