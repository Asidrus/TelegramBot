from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class btnMessage():

    inline_bt_subscr = InlineKeyboardButton("Подписаться на рассылки", callback_data='subscr_newslet')
    inline_kb_subscr = InlineKeyboardMarkup().add(inline_bt_subscr)
    
    inline_bt_group_all = InlineKeyboardButton("Все пользователи", callback_data='all_users')
    inline_bt_group_tester = InlineKeyboardButton("Тестер", callback_data='tester')
