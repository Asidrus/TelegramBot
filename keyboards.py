from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class btnMessage():

    inline_bt_subscr = InlineKeyboardButton("Подписаться на рассылки", callback_data='subscr_newslet')
    inline_kb_subscr = InlineKeyboardMarkup().add(inline_bt_subscr)