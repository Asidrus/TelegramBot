from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
from TelegramBot import TelegramBot
import asyncio
from server import run_server

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


# loop = asyncio.new_event_loop()
# loop.create_task(run_server("localhost", 1234))


# ex = executor.Executor(dp, loop=loop)
ex = executor.Executor(dp)
ex.start_polling()
