from datetime import datetime

import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from libs.telegrambot import TelegramBot
from libs.database import DataBase
import asyncio
from matplotlib import pyplot as plt, use
import random
from credentials import *
from libs.keyboards import btnMessage
from libs.network import Server
import re
from aiogram.dispatcher.filters import Text

bot = TelegramBot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
btnMessage = btnMessage()

db_data = {"user": db_user, "password": db_password, "database": db_name, "host": db_host}


################# КОМАНДЫ ################################

@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    groupUser = await dp.bot.db.get_attrForColumn(columns='group_id', table='users', param=f'id={msg.from_user.id}')
    groupUser = groupUser[0]["group_id"]

    if groupUser == '0':
        await msg.answer("""
        Полный список команд:
        /change_group - сменить группу
        /broadcast [msg] - разослать всем пользователям сообщение
        /out_subscr - посмотреть свои подписки
        /subscribe - подписаться на рассыл0чки
        /leave - покинуть группу
        /help - вывод справки
        /unsubscribe - отписаться от рассыл0чки
        """)

    elif groupUser == '1' or groupUser == '2':
        await msg.answer("""
        Полный список команд:
        /start - активировать чат-бота
        /broadcast [msg] - разослать всем пользователям из своей группы сообщение
        /subscribe - подписаться на рассыл0чки
        /out_subscr - посмотреть свои подписки
        /users - посмотреть всех пользователей в моей группе
        /unsubscribe - отписаться от рассыл0чки
        /help - вывод справки
        /rules - правила бойцовского клуба
        /leave - покинуть группу
        """)

    elif groupUser == '3':
        await msg.answer("""
        Полный список команд:
        /start - активировать чат-бота
        /help - вывод справки
        /enstance [pswd]- вход
        """)


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    res = await dp.bot.db.get_user(msg.from_user.id)
    if len(res) == 0:
        await dp.bot.db.add_user(msg["from"])
        await msg.reply(
            "Добро пожаловать в наш бойцовский клуб! Меня зовут Тостер. Я ваш персональный помощник в дальнейшем. Чтобы узнать о том, что я умею, введите команду /help")

        picture = open('img/toster.jpeg', 'rb')

        await bot.send_photo(chat_id=msg.from_user.id, photo=picture)
    else:
        await msg.answer('Приветствую снова, боец')


@dp.message_handler(commands=['rules'])
async def msg_rules(msg: types.Message):
    await msg.answer(
        f"Первое правило Бойцовского клуба: никому не рассказывать о Бойцовском клубе. \n Второе правило Бойцовского клуба: никогда никому не рассказывать о Бойцовском клубе. \n Третье правило Бойцовского клуба: в схватке участвует только один из команды. Если он не справляется, другие приходят на помощь \n Четвертое правило Бойцовского клуба: оформляй понятные тикеты. \n Пятое правило Бойцовского клуба: бойцы сражаются на тестовом домене.  \n  Седьмое: бой продолжается до тех пор, пока не будут исправлены все баги.  \n  Восьмое и последнее: если вы первый раз в бойцовском клубе, прежде чем вступить в бой, вы должны быть подготовлены к нему и к непонятным ТЗ")
    await bot.send_message(msg.from_user.id,
                               'Выберите УЦ, на который вы хотите подписаться',
                               reply_markup=btnMessage.inline_kb)


# Войти в группу пользователя
@dp.message_handler(commands=['enstance'])
async def group_entry(msg: types.Message):
    groupUser = await dp.bot.matchUser('3', msg.from_user.id)
    res = False
    if groupUser:
        subs = await dp.bot.subscriptionAnalysis(msg.from_user.id)
        text = msg.text.split()
        if len(text) != 1:
            pswd = await dp.bot.db.get_attrForColumn(columns='pswd', table='groups', param="pswd!='None'")
            for rec in pswd:          
                res = await dp.bot.check_password(rec["pswd"], text[1])
                if res:
                    pswd = rec["pswd"]
                    break
            if res:  # если в списке есть пароль
                group = await dp.bot.db.get_attrForColumn(columns='gid', table='groups', param=f"pswd='{pswd}'")
                group = group[0]["gid"]
                if group == '0':
                    picture = open('img/maxresdefault.jpg', 'rb')

                    await msg.answer('Добро пожаловать, господин администратор!')

                    await bot.send_photo(chat_id=msg.from_user.id, photo=picture)
                    await dp.bot.groupTransfer(group=group, column='debug', id=msg.from_user.id)

                elif group == '1':
                    await msg.answer(
                        'Добро пожаловать в ряды тетировщиков! Вам автоматически подключена подписка на рассылку по результатам тестов')
                    await dp.bot.groupTransfer(group=group, column='res_all_tests', id=msg.from_user.id)
                    if not subs:
                        await bot.send_message(msg.from_user.id,
                               'Выберите УЦ, на который вы хотите подписаться',
                               reply_markup=btnMessage.inline_kb_uc_subscription)
                elif group == '2':
                    await msg.answer('Добро пожаловать!')
                    await dp.bot.groupTransfer(group=group, id=msg.from_user.id)
                    if not subs:
                        await bot.send_message(msg.from_user.id, 'Выберите УЦ, на который вы хотите подписаться',
                               reply_markup=btnMessage.inline_kb_uc_subscription)
            else:
                await msg.answer('Неверный пароль')
        else:
            await msg.answer('Введите пароль. Например, "/enstance 123"')
    else:
        await msg.answer('Вы уже вошли')


# Покинуть группу пользователя. Все, кроме 3
@dp.message_handler(commands=['leave'])
async def leave_group(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        if groupUser[1] == '0':
            await dp.bot.db.updateData(column='debug', table='subscribes', param='0', where='uid', id=msg.from_user.id)
        await dp.bot.db.updateData(column='group_id', table='users', param='3', where='id', id=msg.from_user.id)
        await msg.answer('Вы покинули команду')
    else:
        await msg.answer('Вы не можете воспользоваться данной командой')


@dp.message_handler(commands=['change_group'])
async def change_group(msg: types.Message):
    groupUser = await dp.bot.matchUser('0', msg.from_user.id)
    if groupUser:
        await bot.send_message(msg.from_user.id,
                               'Внимание! Вы пытаетесь сменить группу пользователей! Выберите в какую группу вы хотите перейти:',
                               reply_markup=btnMessage.inline_kb_changing_user)
    else:
        await msg.answer('Недостаточно прав')


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
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        text = msg["text"]
        first_name = msg["from"]["first_name"]
        last_name = msg["from"]["last_name"]
        ind = text.find(' ')
        if ind == -1:
            await msg.answer("Пожалуйста, введите текст сообщения. Например '/broadcast Всем привет!'")
        else:
            text = f"""<i>{first_name} {last_name}</i> всем:<b>\n{text[ind + 1:]}</b>"""
            await dp.bot.broadcaster(content=text, id_sender=msg.from_user.id)
    else:
        await msg.answer('Я не понимаю')


@dp.message_handler(commands=['subscribe'])
async def subscribe_user(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        subs = await dp.bot.checkingSubscriptions(groupUser[1], msg.from_user.id)
        if len(subs) == 0:
            await msg.answer(
                'Вы уже подписаны на все предоставляемые нами подписки. Если хотите отписаться, введите команду /unsubscribe')
        else:
            await bot.send_message(msg.from_user.id, 'Выберите подписку на которую вы хотите подписаться:',
                                   reply_markup=await btnMessage.addKeybrd(subs, "sub"))
    else:
        await msg.answer('Недостаточно прав')


@dp.message_handler(commands=['out_subscr'])
async def out_subscribe_for_user(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        subscribes = await dp.bot.checkingSubscriptions(groupUser[1], msg.from_user.id, purpose='out_subscr')
        if len(subscribes)==0:
            await msg.answer('У вас нет активных подписок. Чтобы подписаться на рассылку введите команду /subscribe')
        else:
            await msg.answer(
                f'Вы подписаны на следующие рассылки: {subscribes}. Чтобы отписаться от какой-нибудь рассылки, введите команду /unsubscribe')
    else:
        await msg.answer('Недостаточно прав')


@dp.message_handler(commands=['users'])
async def out_subscribe_for_user(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    users = ''
    if groupUser[0]:
        usrName = await dp.bot.db.get_attrForColumn(columns='first_name', table='users',
                                                    param=f"group_id='{groupUser[1]}' and id!='{msg.from_user.id}'")
        usrName = [rec["first_name"] for rec in usrName]
        for user in usrName:
            users = users + user + '\n'  # <- делаем строку
        await msg.answer(f'Пользователи в вашей группе: {users}')
    else:
        await msg.answer('Недостаточно прав')


@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        subs = await dp.bot.checkingSubscriptions(groupUser[1], msg.from_user.id)
        if len(subs) == 0:
            await msg.anwer('У вас нет активных подписок. Чтобы подписаться на рассылки, введите команду /subscribe')
        else:
            await bot.send_message(msg.from_user.id, 'Выберите рассылку от которой хотите отписаться',
                                   reply_markup=await btnMessage.addKeybrd(subs, "unsub"))
    else:
        await msg.answer('Недостаточно прав')


################# ТЕКСТ ################################

@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
        await msg.answer('Привет!')
    else:
        await msg.answer('Не понимаю, что это значит.')


################# КНОПОНЬКИ ################################

# Подписка на все тесты
# @dp.callback_query_handler(text='subscr_all_test')
# async def subscription_tester(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='res_all_tests', table='subscribes', param='1', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вам оформлена подписка на тесты')


# # Подписка на рассылку All
# @dp.callback_query_handler(text='subscr_all_users')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='from_users', table='subscribes', param='1', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вам оформлена подписка на общую рассылку')


# # Подписка на penta
# @dp.callback_query_handler(text='subscr_penta')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='rt_penta', table='subscribes', param='1', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вам оформлена подписка на pentaschool')

# # Подписка на psy
# @dp.callback_query_handler(text='subscr_psy')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='rt_psy', table='subscribes', param='1', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вам оформлена подписка на PSY')

# # Подписка на psy
# @dp.callback_query_handler(text='subscr_mult')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='rt_mult', table='subscribes', param='1', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вам оформлена подписка на мультидвижок')

# # Подписка на debug
# @dp.callback_query_handler(text='subscr_debug')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='debug', table='subscribes', param='1', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вам оформлена подписка на дебаг')


# # Отписаться от debug
# @dp.callback_query_handler(text='unsubscr_debug')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='debug', table='subscribes', param='0', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы отписались от рассылки дебага')

# # Отписаться от penta
# @dp.callback_query_handler(text='unsubscr_penta')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='rt_penta', table='subscribes', param='0', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы отписались от рассылки тестов pentaschool')

# # Отписаться от psy
# @dp.callback_query_handler(text='unsubscr_psy')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='rt_psy', table='subscribes', param='0', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы отписались от рассылки тестов по psy')

# # Отписаться от mult
# @dp.callback_query_handler(text='unsubscr_mult')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='rt_mult', table='subscribes', param='0', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы отписались от рассылки тестов по mult')

# #  Отписаться от рассылки результатов тестов
# @dp.callback_query_handler(text='unsubscr_all_test')
# async def subscription_tester(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='res_all_tests', table='subscribes', param='0', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы отписались от рассылки по результатам всех тестов')


# # Отписаться от рассылки All
# @dp.callback_query_handler(text='unsubscr_all_users')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='from_users', table='subscribes', param='0', where='uid',
#                                id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы отписались от общей рассылки')


# # Подписка на группу тестеров
# @dp.callback_query_handler(text='user_tester')
# async def subscription_tester(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='debug', param='0', table='subscribes', where='uid',
#                                id=callback_query.from_user.id)
#     await dp.bot.db.updateData(column='group_id', table='users', param='1', where='id', id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы перешли в группу тестеров')


# # Подписка на группу All
# @dp.callback_query_handler(text='users_all')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
#     await dp.bot.db.updateData(column='debug', param='0', table='subscribes', where='uid',
#                                id=callback_query.from_user.id)
#     await dp.bot.db.updateData(column='group_id', table='users', param='2', where='id', id=callback_query.from_user.id)
#     await bot.send_message(callback_query.from_user.id, 'Вы перешли в общую группу')


# @dp.callback_query_handler(text='dont_want')
# async def subscription_all_users(callback_query: types.CallbackQuery):
#     await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)


@dp.callback_query_handler(Text(startswith="subs_"))
async def callbacks_num(call: types.CallbackQuery):
    user_value = call.from_user.id
    action = call.data[5:]
    print(user_value, action)

################# КАКАЯ ТО ХЕРНЯ #################################

async def getNotes(conn, url, From, To):
    # print(f"select * from timings,urls where datetime between '{From}' and '{To}' and urls.url='{url}';")
    res = await conn.fetch(
        f"select * from timings,urls where datetime between '{From}' and '{To}' and urls.url='{url}';")
    return res


################# БОСС заПУСКА #################################

def main():
    bot.db = DataBase()
    server = Server(socket_ip, socket_port, handler=bot.broadcaster)

    loop = asyncio.new_event_loop()
    loop.create_task(server.runSever())
    # loop.create_task(bot.db.run_db())
    asyncio.set_event_loop(loop)
    ex = executor.Executor(dp, loop=loop)
    ex.start_polling()


if __name__ == "__main__":
    main()