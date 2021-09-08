from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
from TelegramBot import TelegramBot
import asyncio
# from server import run_server

API_TOKEN = "1924016224:AAF4TufT_s-WLu5a1WbXOl04NL9Wfq0MpEI"
bot = TelegramBot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
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

# counter = 0
#
#
# async def serve_client(reader, writer):
#     global counter
#     cid = counter
#     counter += 1  # Потоко-безопасно, так все выполняется в одном потоке
#     print(f'Client #{cid} connected')
#
#     request = await read_request(reader)
#     if request is None:
#         print(f'Client #{cid} unexpectedly disconnected')
#     else:
#         response = await handle_request(request)
#         await write_response(writer, response, cid)
#
#
# async def handle_request(request):
#     await asyncio.sleep(5)
#     return request[::-1]
#
#
# async def read_request(reader, delimiter=b'!'):
#     request = bytearray()
#     while True:
#         chunk = await reader.read(4)
#         if not chunk:
#             # Клиент преждевременно отключился.
#             break
#         request += chunk
#         if delimiter in request:
#             return request
#     return None
#
#
# async def write_response(writer, response, cid):
#     await bot.broadcaster(response)
#     print(response)
#     writer.write(response)
#     await writer.drain()
#     writer.close()
#     print(f'Client #{cid} has been served')
#
#
# async def run_server(host, port):
#     server = await asyncio.start_server(serve_client, host, port)
#     await server.serve_forever()


loop = asyncio.new_event_loop()
loop.create_task(bot.run_server("localhost", 1234))


ex = executor.Executor(dp, loop=loop)
# ex = executor.Executor(dp)
ex.start_polling()
