from datetime import datetime

import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from libs.telegrambot import TelegramBot
from libs.database import DataBase
import asyncio
from matplotlib import pyplot as plt
import random
from credentials import *

bot = TelegramBot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

db_data = {"user": db_user, "password": db_password, "database": db_name, "host": db_host}


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


async def getNotes(conn, url, From, To):
    print(f"select * from timings,urls where datetime between '{From}' and '{To}' and urls.url='{url}';")
    res = await conn.fetch(
        f"select * from timings,urls where datetime between '{From}' and '{To}' and urls.url='{url}';")
    return res


@dp.message_handler(commands=['test'])
async def __test__(msg: types.Message):
    interval = msg.text.replace('/test ', "")
    t1 = interval[:interval.find("-")]
    t2 = interval[interval.find("-") + 1:]
    try:
        date1 = datetime.strptime(t1, '%m/%d/%Y')
        date2 = datetime.strptime(t2, '%m/%d/%Y')
    except Exception as e:
        await msg.answer("Введите в формате: /test 01/01/2021-12/31/2021")
        return 0
    connection = await asyncpg.connect(user=db_user,
                                       password=db_password,
                                       database="speedtest",
                                       host="localhost")

    res = await getNotes(connection, "https://pentaschool.ru", t1, t2)
    days = (date2 - date1).days
    data = []
    for i in range(days):
        data.append([(rec["speed"].microsecond / 1000.0 + rec["speed"].second) for rec in res if
                     ((rec["datetime"] - date1).days >= i) and ((rec["datetime"] - date1).days < (i + 1))])
    if len(res) == 0:
        await msg.answer("По данному диапозону не найдено тестов")
    else:
        await connection.close()
        # plt.plot([(rec["speed"].microsecond / 1000.0 + rec["speed"].second) for rec in res])

        fig4, ax4 = plt.subplots()
        ax4.set_title('Hide Outlier Points')
        ax4.boxplot(data, showfliers=False)

        fname = f"../temp/{random.randint(0, 2 ** 32)}.png"
        plt.savefig(fname)
        await bot.send_photo(chat_id=msg.from_user.id, photo=open(fname, 'rb'))


@dp.message_handler(commands=['broadcast'])
async def send_broadcast(msg: types.Message):
    text = msg["text"]
    first_name = msg["from"]["first_name"]
    last_name = msg["from"]["last_name"]
    text = f"""<i>{first_name} {last_name}</i> всем:<b>\n{text[text.find(' ') + 1:]}</b>"""
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
    loop.create_task(bot.run_server(socket_ip, socket_port))
    asyncio.set_event_loop(loop)
    ex = executor.Executor(dp)
    ex.start_polling()


if __name__ == "__main__":
    main()

