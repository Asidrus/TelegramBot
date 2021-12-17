from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class btnMessage():
    
 
    inline_bt_subscr_penta = InlineKeyboardButton("Мультидвижок", callback_data='subs_Мультидвижок')
    inline_bt_subscr_psy = InlineKeyboardButton("PSY", callback_data='subs_PSY')
    inline_bt_subscr_mult = InlineKeyboardButton("Pentaschool", callback_data='subs_Pentaschool')
    inline_bt_subscr_want = InlineKeyboardButton("Не хочу", callback_data='dont_want')
    inline_kb_uc_subscription = InlineKeyboardMarkup(row_width=2).row(inline_bt_subscr_penta, inline_bt_subscr_psy, inline_bt_subscr_mult,inline_bt_subscr_want)


    inline_bt_user_tester = InlineKeyboardButton("Тесты", callback_data='user_tester')
    inline_bt_users_all = InlineKeyboardButton("Общая группа", callback_data='users_all')
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