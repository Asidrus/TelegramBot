from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import TelegramBot
from TelegramBot import TelegramBot, read_users, write_users, users, DataBase
import asyncio

API_TOKEN = "1924016224:AAF4TufT_s-WLu5a1WbXOl04NL9Wfq0MpEI"
bot = TelegramBot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


# @dp.message_handler(commands=['start', 'help'])
# async def send_welcome(msg: types.Message):
#
#     await msg.reply_to_message(f"Я бот. Приятно познакомиться,{msg.from_user.first_name}")

@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    await msg.answer("""
    Полный список команд:
    /start - подписаться на рассылки
    /unsubscribe - отписаться от рассылок
    /broadcast [msg] - разослать всем рассылку
    """)


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    res = await dp.bot.db.get_user(msg.from_user.id)
    if len(res) == 0:
        await dp.bot.db.add_user(msg["from"])
        await msg.answer("Вы успешно подписаны на оповещения!\nЧтобы отписаться воспользуйтесь /unsubscribe")
    else:
        await msg.answer("Вы уже подписаны\nЧтобы отписаться воспользуйтесь /unsubscribe")


@dp.message_handler(commands=['broadcast'])
async def send_broadcast(msg: types.Message):
    print(msg)
    text = msg["text"]
    first_name = msg["from"]["first_name"]
    last_name = msg["from"]["last_name"]
    text = f"""<i>{first_name} {last_name}</i> всем:<b>\n{text[text.find(' ')+1:]}</b>"""
    await dp.bot.broadcaster(text)


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
        await msg.answer('Привет!')
    else:
        await msg.answer('Не понимаю, что это значит.')


def main():
    bot.db = DataBase()
    loop = asyncio.new_event_loop()
    loop.create_task(bot.run_server("localhost", 1234))
    loop.create_task(bot.db.run_db())
    ex = executor.Executor(dp, loop=loop)
    ex.start_polling()


def _test(test_id):
    with open("ids", "r") as r:
        data = r.readlines()
    print(data)
    # test_id = '936364717'
    if any([test_id == id[:-1] for id in data]):
        print("id exists")
    else:
        with open("ids", "a") as w:
            w.writelines(test_id+"\n")
        data.append(test_id+"\n")
    print(data)


if __name__ == "__main__":
    main()
    # _test('936364716')


