from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from time import sleep
import socket


class TelegramBot():
    TOKEN = "1924016224:AAF4TufT_s-WLu5a1WbXOl04NL9Wfq0MpEI"
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)
    id = 936364717

    def __init__(self):
        import socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", 5678))
        self.server.listen(5)
        print("listen")
        self.serv()
        executor.start_polling(self.dp)

    def serv(self):
        while True:
            user_socket, address = self.server.accept()
            print(f"User {user_socket} connected")
            user_socket.send("Connected".encode())
            data = user_socket.recv(1024)
            self.dp.bot.send_message(self.id, data)
            print(data.decode("utf-8"))


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

    async def send(dispatcher, msg):
        await dispatcher.bot.send_mesage(id, msg)
