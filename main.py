from datetime import datetime

import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from keyboards import btnMessage
from libs.telegrambot import TelegramBot
from libs.database import DataBase
import asyncio
from matplotlib import pyplot as plt, use
import random
from credentials import *
from keyboards import btnMessage

bot = TelegramBot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
btnMessage = btnMessage()

db_data = {"user": db_user, "password": db_password, "database": db_name, "host": db_host}


@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    groupUser = await dp.bot.db.get_attrForColummn(columns='group_id',table='users', param=f'uid={msg.from_user.id}')

    if groupUser == '0':
        await msg.answer("""
        Полный список команд:
        /change_group - сменить группу
        /broadcast [msg] - разослать всем пользователям сообщение
        /out_subscr - посмотреть свои подписки
        /chande_subscr - сменить подписки
        """)

    elif groupUser=='1' or groupUser=='2':
        await msg.answer("""
        Полный список команд:
        /start - активировать чат-бота
        /broadcast [msg] - разослать всем пользователям из своей группы сообщение
        /subscribe - подписаться на рассыл0чки
        /users - посмотреть всех пользователей в моей группе
        /unsubscribe - отписаться от рассыл0чки
        /rules - правила бойцовского клуба
        /leave - покинуть группу
        """)
    
    elif groupUser == '3':
        await msg.answer("""
        Полный список команд:
        /start - активировать чат-бота
        /broadcast [msg] - разослать всем пользователям сообщение
        /entance - вход
        """)

@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    
    res = await dp.bot.db.get_user(msg.from_user.id)
    if len(res) == 0:
        await dp.bot.db.add_user(msg["from"])
        await msg.reply("Добро пожаловать в наш бойцовский клуб! Меня зовут Тостер. Я ваш персональный помощник в дальнейшем. Чтобы узнать о том, что я умею, введите команду /help", reply_markup=btnMessage.inline_kb_subscr)
    else:
        await msg.answer('Приветствую снова, боец')

@dp.callback_query_handler(text='subscr_newslet')
async def subscriptionProcess(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, 'Выберите подписку на которую вы хотите подписаться:')

@dp.message_handler(commands=['rules'])
async def send_welcome(msg: types.Message):
    
    await msg.send_message(msg.from_user.id, r"Первое правило Бойцовского клуба: никому не рассказывать о Бойцовском клубе. \n Второе правило Бойцовского клуба: никогда никому не рассказывать о Бойцовском клубе. \n Третье правило Бойцовского клуба: в схватке участвует только один из команды. Если он не справляется, другие приходят на помощь \n Четвертое правило Бойцовского клуба: оформляй понятные тикеты. \n Пятое правило Бойцовского клуба: бойцы сражаются на тестовом домене.  \n  Седьмое: бой продолжается до тех пор, пока не будут исправлены все баги.  \n  Восьмое и последнее: если вы первый раз в бойцовском клубе, прежде чем вступить в бой, вы должны быть подготовлены к нему и к непонятным ТЗ")

@dp.message_handler(commands=['entance'])
async def send_welcome(msg: types.Message):
    await msg.answer('Чтобы продолжить, пожалуйста, введите пароль:')

@dp.message_handler(commands=['change_group'])
async def send_welcome(msg: types.Message):
    await msg.answer('Внимание! Вы пытаетесб сменить группу поользователей! Выберите в какую группу вы хотите перейти:')


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
    await dp.bot.broadcaster(msg=text, id_sender=msg.from_user.id)

@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
        await msg.answer('Привет!')
    else:
        pswd = await dp.bot.get_attrForColummn(columns='pswd', table='group')

        for item in pswd:
            if msg.text == item:
                group = await dp.bot.get_attrForColummn(columns='gid', table='group')

                if group == '0':
                    photo = open('maxresdefault.jpg', 'rb')
                    msg.answer('Добро пожаловать, господин администратор!')
                    await msg.send_photo(msg.from_user.id, photo)

                    await  dp.bot.groupTransfer(group,column='debug', id=msg.from_user.id)

                elif group == '1':
                    await msg.answer('Добро пожаловать в ряды тетировщиков!')
                    await dp.bot.updateData
                    
                    await  dp.bot.groupTransfer(group,column='result_test', id=msg.from_user.id)
   
                elif group == '2':
                    await msg.answer('Добро пожаловать!')
                    await  dp.bot.groupTransfer(group=group, id=msg.from_user.id)
                    
    
  

        await msg.answer('Не понимаю, что это значит.')


def main():
    bot.db = DataBase()
    loop = asyncio.new_event_loop()
    loop.create_task(bot.run_server(socket_ip, socket_port))
    # loop.create_task(bot.db.run_db())
    asyncio.set_event_loop(loop)
    ex = executor.Executor(dp, loop=loop)
    ex.start_polling()


if __name__ == "__main__":
    main()

