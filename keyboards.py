from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class btnMessage():

    inline_bt_subscr = InlineKeyboardButton("Подписаться на рассылки", callback_data='subscr_newslet')
 
    inline_bt_group_all = InlineKeyboardButton("Все", callback_data='subscr_all_users')

    inline_bt_group_tester = InlineKeyboardButton("Тесты", callback_data='subscr_tester')


    inline_kb_offer_subscr = InlineKeyboardMarkup().add(inline_bt_subscr)
   
    inline_kb_subscr = InlineKeyboardMarkup(row_width=2)

    inline_kb_subscr.row(inline_bt_group_tester, inline_bt_group_all)
