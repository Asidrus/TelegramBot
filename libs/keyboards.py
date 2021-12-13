from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class btnMessage():
    
    # inline_bt_subscr_all = InlineKeyboardButton("Общие рассылки", callback_data='subscr_all_users')
    # inline_bt_subscr_all_test = InlineKeyboardButton("Все тесты", callback_data='subscr_all_test')
    # inline_bt_subscr_debug = InlineKeyboardButton("Дебаг", callback_data='subscr_debug')
    
    inline_bt_subscr_penta = InlineKeyboardButton("Мультидвижок", callback_data='subscr_mult')
    inline_bt_subscr_psy = InlineKeyboardButton("PSY", callback_data='subscr_psy')
    inline_bt_subscr_mult = InlineKeyboardButton("Pentaschool", callback_data='subscr_penta')

    # inline_bt_unsubscr_all = InlineKeyboardButton("Общие", callback_data='unsubscr_all_users')
    # inline_bt_unsubscr_all_test = InlineKeyboardButton("Тесты", callback_data='unsubscr_all_test')
    # inline_bt_unsubscr_debug = InlineKeyboardButton("Дебаг", callback_data='unsubscr_debug')
    # inline_bt_unsubscr_penta = InlineKeyboardButton("Pentaschool", callback_data='unsubscr_penta')
    # inline_bt_unsubscr_psy = InlineKeyboardButton("PSY", callback_data='unsubscr_psy')
    # inline_bt_unsubscr_mult = InlineKeyboardButton("Мультидвижок", callback_data='unsubscr_mult')


    inline_bt_user_tester = InlineKeyboardButton("Тесты", callback_data='user_tester')
    inline_bt_users_all = InlineKeyboardButton("Общая группа", callback_data='users_all')
    
    inline_bt_subscr_want = InlineKeyboardButton("Не хочу", callback_data='dont_want')

    inline_kb_uc_subscription = InlineKeyboardMarkup(row_width=2).row(inline_bt_subscr_penta, inline_bt_subscr_psy, inline_bt_subscr_mult,inline_bt_subscr_want)

    inline_kb_changing_user = InlineKeyboardMarkup().row(inline_bt_user_tester,inline_bt_users_all)

    async def addKeybrd(self, subscribes, flag=''):
        count = 0
        inline_kb_full = InlineKeyboardMarkup(row_width=2)
        for key in subscribes.keys():
            if subscribes[key] and flag=='_':
                inline_kb_full.add(InlineKeyboardButton(key, callback_data='subs_'+key+flag))
                count = count+1
            elif not subscribes[key] and flag=='':
                inline_kb_full.add(InlineKeyboardButton(key, callback_data='subs_'+key+flag))
                count = count+1
        return [inline_kb_full, count]