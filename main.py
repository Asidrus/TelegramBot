from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from TelegramBot import TelegramBot
import asyncio

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


def main():
    loop = asyncio.new_event_loop()
    loop.create_task(bot.run_server("localhost", 1234))

    ex = executor.Executor(dp, loop=loop)
    ex.start_polling()


def _test():
    with open("ids", "r") as r:
        data = r.readlines()
    print(data)
    test_id = '936364717'
    print([test_id == id[:-2] for id in data])


if __name__ == "__main__":
    # main()
    _test()


