import asyncio
import logging
from threading import Thread

from aiogram import Bot, Dispatcher, types
from aiogram.utils import exceptions, executor
from server import *

API_TOKEN = "1924016224:AAF4TufT_s-WLu5a1WbXOl04NL9Wfq0MpEI"
logging.basicConfig(level=logging.INFO)
log = logging.getLogger('broadcast')
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
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


def get_users():
    """
    Return users list

    In this example returns some random ID's
    """
    yield from (936364717, )


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        log.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        log.error(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        log.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        log.exception(f"Target [ID:{user_id}]: failed")
    else:
        log.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcaster(msg) -> int:
    """
    Simple broadcaster

    :return: Count of messages
    """
    count = 0
    try:
        for user_id in get_users():
            if await send_message(user_id, f'<a>{msg.decode()}!</a>'):
                count += 1
            await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
    finally:
        log.info(f"{count} messages successful sent.")

    return count


if __name__ == '__main__':
    # asyncio.run(run_server('127.0.0.1', 1234))
    serv = Thread(target=asyncio.run, args=(run_server('127.0.0.1', 1234),))
    serv.start()
    executor.start_polling(dp)