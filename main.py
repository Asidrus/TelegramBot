from aiogram import Dispatcher, types
from aiogram.utils import executor
from libs.telegrambot import TelegramBot
from libs.database import DataBase
import asyncio
from matplotlib import pyplot as plt, use
from libs.keyboards import btnMessage
from libs.network import Server
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentType
import os
import help

""" Read env """
from dotenv import load_dotenv
load_dotenv()

ENV_LOCAL = '.env_local'
if os.path.isfile(ENV_LOCAL):
    load_dotenv(ENV_LOCAL)


# PROJECT_NAME = os.getenv('PROJECT')
# STORAGE_PATH = os.getenv('STORAGE')
# IP = os.getenv('IP')
# PORT = os.getenv('PORT')
DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
API_TOKEN = os.getenv('API_TOKEN')

bot = TelegramBot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)
btnMessage = btnMessage()

db_data = {"user": DB_NAME, "password": DB_PASSWORD, "database": DB_NAME, "host": DB_HOST}


################# КОМАНДЫ ################################

@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    groupUser = await dp.bot.db.get_attrForColumn(columns='group_id', table='users', param=f'id={msg.from_user.id}')
    groupUser = groupUser[0]["group_id"]
    for key in help.dick_help.key():
        if key==groupUser:
            await msg.answer(help)


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


# Войти в группу пользователя
@dp.message_handler(commands=['signin'])
async def group_entry(msg: types.Message):
    groupUser = await dp.bot.matchUser('3', msg.from_user.id)
    res = False
    if groupUser:
        subs = await dp.bot.checkingSubscriptions(msg.from_user.id, purpose='УЦ')
        text = msg.text.split()
        if len(text) != 1:
            pswd = await dp.bot.db.get_attrForColumn(columns='pswd, id', table='groups', param="pswd!='None'")
            pswd = [dict(row) for row in pswd]
            for rec in pswd: 
                if dp.bot.check_password(rec["pswd"], text[1]):
                    group = rec["id"]
                    break
                
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
            await msg.answer('Введите пароль. Например, "/signin 123"')
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


@dp.message_handler(commands=['all', 'penta', 'psy', 'mult', 'osek'])
async def send_broadcast(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id)
    if groupUser:
        text = msg["text"]
        first_name = msg["from"]["first_name"]
        last_name = msg["from"]["last_name"]
        ind = text.find(' ')
  
        if ind == -1 or len(text)<=5:
            await msg.answer("Пожалуйста, введите текст сообщения. Например, '/all Всем привет!'")
        else:
            text = f"""<i>{first_name} {last_name}</i> для {text[1:ind]}<b>\n{text[ind + 1:]}</b>"""
            await dp.bot.broadcaster(content=text, id_sender=msg.from_user.id, project=msg['text'][1:ind])
    else:
        await msg.answer('Я не понимаю')


@dp.message_handler(commands=['broadcast'])
async def subscribe_user(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        await msg.answer(
                'Привет! Эта команда больше недоступна. Вместо нее можно использовать команды /all, /penta, /psy, /mult, /osek. Более подробную информацию можно посмотреть в /help')
       
    else:
        await msg.answer('Недостаточно прав')



@dp.message_handler(commands=['subscribe'])
async def subscribe_user(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        subs_kwrd = await btnMessage.addKeybrd(await dp.bot.checkingSubscriptions(msg.from_user.id, group=groupUser[1], purpose='subs'))
        if subs_kwrd[1] == 0:
            await msg.answer(
                'Вы уже подписаны на все предоставляемые нами подписки. Если хотите отписаться, введите команду /unsubscribe')
        else:
            await bot.send_message(msg.from_user.id, 'Выберите подписку на которую вы хотите подписаться:', reply_markup=subs_kwrd[0])
    else:
        await msg.answer('Недостаточно прав')


@dp.message_handler(commands=['out_subscr'])
async def out_subscribe_for_user(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    if groupUser[0]:
        subscribes = await dp.bot.checkingSubscriptions(msg.from_user.id, group=groupUser[1], purpose='my_subs')
        if len(subscribes)==0:
            await msg.answer('У вас нет активных подписок. Чтобы подписаться на рассылку введите команду /subscribe')
        else:
            await msg.answer(
                f'Вы подписаны на следующие рассылки: {subscribes}. Чтобы отписаться от какой-нибудь рассылки, введите команду /unsubscribe')
    else:
        await msg.answer('Недостаточно прав')


@dp.message_handler(commands=['users'])
async def withdrawal_of_classmates(msg: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], msg.from_user.id, back_group=True)
    users = ''
    if groupUser[0]:
        usrName = await dp.bot.db.get_attrForColumn(columns='first_name', table='users', param=f"group_id='{groupUser[1]}' and id!='{msg.from_user.id}'")

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
        subs_kwd = await btnMessage.addKeybrd(await dp.bot.checkingSubscriptions(msg.from_user.id, group=groupUser[1], purpose='subs'), "_") 
        if subs_kwd[1] == 0:
            await msg.answer('У вас нет активных подписок. Чтобы подписаться на рассылки, введите команду /subscribe')
        else:
            await bot.send_message(msg.from_user.id, 'Выберите рассылку от которой хотите отписаться',
                                   reply_markup=subs_kwd[0])
    else:
        await msg.answer('Недостаточно прав')


################# ОТ ПОЛЬЗОВАТЕЛЯ ################################

@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    if msg.text.lower() == 'привет':
        await msg.answer('Привет!')
    else:
        await msg.answer('Не понимаю, что это значит. Но ты можешь заглянуть в /help - тут описаны все мои возможности')

@dp.message_handler(content_types=ContentType.ANY)
async def media_handler(message: types.Message):
    groupUser = await dp.bot.matchUser(['0', '1', '2'], message.from_user.id)
    if groupUser:
        if  message.caption!=None:
            caption = message.caption

            ind = caption.find(' ')

            if ind!=-1:
                command = caption[1:ind] 
                text = f"""<i>{ message["from"]["first_name"]} { message["from"]["last_name"]}</i> для {command}:<b>\n{caption[ind + 1:]}</b>"""
            else:
                command = caption[1:]
                text = f"""<i>{ message["from"]["first_name"]} { message["from"]["last_name"]}</i> для {command}:"""

            if command == 'penta' or command == 'psy' or command == 'mult' or command == 'all' or command == 'osek':
                
                if message.photo:
                    
                    document_id = message.photo[0].file_id
                    file_info = await bot.get_file(document_id)

                    await dp.bot.broadcaster(content=text, id_sender=message.from_user.id, project=command, id_media={'photo':file_info.file_id})

                elif message.animation:
                  
                    await dp.bot.broadcaster(content=text, id_sender=message.from_user.id, project=command, id_media={'animation':message.animation.file_id})
                
                elif message.video:

                    await dp.bot.broadcaster(content=text, id_sender=message.from_user.id, project=command, id_media={'video':message.video.file_id})

        else:

            await message.answer('Пожалуйста, введите команду при отправке медиа файлов. Например, /all или /all [msg]')
        

    else:
        await message.answer('Не понимаю')


################# КНОПОНЬКИ ################################

# Подписка на группу тестеров
@dp.callback_query_handler(text='user_tester')
async def subscription_tester(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await dp.bot.db.updateData(column='debug', param='0', table='subscribes', where='uid',
                               id=callback_query.from_user.id)
    await dp.bot.db.updateData(column='group_id', table='users', param='1', where='id', id=callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, 'Вы перешли в группу тестеров')


# Подписка на группу All
@dp.callback_query_handler(text='users_all')
async def subscription_all_users(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await dp.bot.db.updateData(column='debug', param='0', table='subscribes', where='uid',
                               id=callback_query.from_user.id)
    await dp.bot.db.updateData(column='group_id', table='users', param='2', where='id', id=callback_query.from_user.id)
    await bot.send_message(callback_query.from_user.id, 'Вы перешли в общую группу')


# Кнопонька Не хочу
@dp.callback_query_handler(text='dont_want')
async def subscription_all_users(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

# Кнопонька ДА. Повторная подписка
@dp.callback_query_handler(text='subscribe')
async def repeated_withdrawal_of_subscriptions(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    groupUser = await dp.bot.matchUser(['0', '1', '2'], callback_query.from_user.id, back_group=True)
    if groupUser[0]:
        subs_kwrd = await btnMessage.addKeybrd(await dp.bot.checkingSubscriptions(callback_query.from_user.id, group=groupUser[1], purpose='subs'))
        if subs_kwrd[1] == 0:
            await bot.send_message(callback_query.from_user.id,
                'Вы уже подписаны на все предоставляемые нами подписки. Если хотите отписаться, введите команду /unsubscribe')
        else:
            await bot.send_message(callback_query.from_user.id, 'Выберите подписку на которую вы хотите подписаться:', reply_markup=subs_kwrd[0])
    else:
        await callback_query.answer('Недостаточно прав')

# Кнопонька ДА. Повторная отписка
@dp.callback_query_handler(text='unsubscribe')
async def subscription_all_users(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    groupUser = await dp.bot.matchUser(['0', '1', '2'], callback_query.from_user.id, back_group=True)
    if groupUser[0]:
        subs_kwd = await btnMessage.addKeybrd(await dp.bot.checkingSubscriptions(callback_query.from_user.id, group=groupUser[1], purpose='subs'), "_") 
        if subs_kwd[1] == 0:
            await bot.send_message(callback_query.from_user.id, 'У вас нет активных подписок. Чтобы подписаться на рассылки, введите команду /subscribe')
        else:
            await bot.send_message(callback_query.from_user.id, 'Выберите рассылку от которой хотите отписаться',
                                   reply_markup=subs_kwd[0])
    else:
        await callback_query.answer('Недостаточно прав')



# Подписаться, отписаться
@dp.callback_query_handler(Text(startswith="subs_"))
async def callbacks_num(call: types.CallbackQuery):
    await bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    action = call.data[5:]
    if '_' in action:
        action = action[:-1]
        res = await dp.bot.workSubscribes(uid=call.from_user.id, act=action, flag="_")
        if res:
            await bot.send_message(call.from_user.id, f'Вы отписались от {action}')
            await bot.send_message(call.from_user.id, 'Хотите отписаться от еще одной рассылки?', reply_markup=btnMessage.inline_bt_unsubscr_agreement)
        else:
            await bot.send_message(call.from_user.id, 'Что то пошло не так')
            
    else:
        res = await dp.bot.workSubscribes(uid=call.from_user.id, act=action)
        if res:
            await bot.send_message(call.from_user.id, f'Вам оформлена подписка на {action}')
            await bot.send_message(call.from_user.id, 'Хотите подписаться на еще одну рассылку?', reply_markup=btnMessage.inline_bt_subscr_agreement)
        else:
            await bot.send_message(call.from_user.id,'Что то пошло не так')   



################# БОСС заПУСКА #################################

def main():
    bot.db = DataBase()
    server = Server("0.0.0.0", 1111, handler=bot.broadcaster)

    loop = asyncio.new_event_loop()
    loop.create_task(server.runSever())
    # loop.create_task(bot.db.run_db())
    asyncio.set_event_loop(loop)
    ex = executor.Executor(dp, loop=loop)
    ex.start_polling()


if __name__ == "__main__":
    main()