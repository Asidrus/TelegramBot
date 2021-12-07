from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class btnMessage():
    
    inline_bt_subscr_all = InlineKeyboardButton("Общие рассылки", callback_data='subscr_all_users')
    inline_bt_subscr_all_test = InlineKeyboardButton("Все тесты", callback_data='subscr_all_test')
    inline_bt_subscr_debug = InlineKeyboardButton("Дебаг", callback_data='subscr_debug')
    
    inline_bt_subscr_penta = InlineKeyboardButton("Мультидвижок", callback_data='subscr_mult')
    inline_bt_subscr_psy = InlineKeyboardButton("PSY", callback_data='subscr_psy')
    inline_bt_subscr_mult = InlineKeyboardButton("Pentaschool", callback_data='subscr_penta')

    inline_bt_unsubscr_all = InlineKeyboardButton("Общие", callback_data='unsubscr_all_users')
    inline_bt_unsubscr_all_test = InlineKeyboardButton("Тесты", callback_data='unsubscr_all_test')
    inline_bt_unsubscr_debug = InlineKeyboardButton("Дебаг", callback_data='unsubscr_debug')
    inline_bt_unsubscr_penta = InlineKeyboardButton("Pentaschool", callback_data='unsubscr_penta')
    inline_bt_unsubscr_psy = InlineKeyboardButton("PSY", callback_data='unsubscr_psy')
    inline_bt_unsubscr_mult = InlineKeyboardButton("Мультидвижок", callback_data='unsubscr_mult')


    inline_bt_user_tester = InlineKeyboardButton("Тесты", callback_data='user_tester')
    inline_bt_users_all = InlineKeyboardButton("Общие рассылки", callback_data='users_all')
    
    inline_bt_subscr_want = InlineKeyboardButton("Не хочу", callback_data='dont_want')

    inline_kb_uc_subscription = InlineKeyboardMarkup(row_width=2).row(inline_bt_subscr_penta, inline_bt_subscr_psy, inline_bt_subscr_mult,inline_bt_subscr_want)

    inline_kb_changing_user = InlineKeyboardMarkup().row(inline_bt_user_tester,inline_bt_users_all)



    inline_bt_unsubscr = InlineKeyboardButton("Кнопонька", callback_data='subs_xyinyA')
    inline_bt_unsub = InlineKeyboardButton("Кнопонька 2", callback_data='subs_xyinyA2')
    inline_kb = InlineKeyboardMarkup().row(inline_bt_unsubscr, inline_bt_unsub)


    async def addKeybrd(self, kb, key):
        inline_kb_full = InlineKeyboardMarkup(row_width=2)
        if key == 'sub':
            for i in kb:
                if i=='from_users':
                    inline_kb_full.add(self.inline_bt_subscr_all)
                elif i == 'debug':
                    inline_kb_full.add(self.inline_bt_subscr_debug)
                elif i == 'res_all_tests':
                    inline_kb_full.add(self.inline_bt_subscr_all_test)
                elif  i == 'rt_psy':
                    print('rt_psy')
                    inline_kb_full.add(self.inline_bt_subscr_psy)
                elif i == 'rt_penta':
                    inline_kb_full.add(self.inline_bt_subscr_penta)
                elif i == 'rt_mult':
                    inline_kb_full.add(self.inline_bt_subscr_mult)
        else:
            for i in kb:
                if i =='from_users':
                    inline_kb_full.add(self.inline_bt_unsubscr_all)
                elif i == 'debug':
                    inline_kb_full.add(self.inline_bt_unsubscr_debug)
                elif i == 'res_all_tests':
                    inline_kb_full.add(self.inline_bt_unsubscr_all_test)
                elif  i == 'rt_psy':
                    inline_kb_full.add(self.inline_bt_unsubscr_psy)
                elif i == 'rt_penta':
                    inline_kb_full.add(self.inline_bt_unsubscr_penta)
                elif i == 'rt_mult':
                    inline_kb_full.add(self.inline_bt_unsubscr_mult)
        return inline_kb_full

    async def TANYA_MOJNO_PISAT_KOROCHE(self, subscribes, flag):
        flag = '' if flag == True else "_"
        inline_kb_full = InlineKeyboardMarkup(row_width=2)
        for key in subscribes.keys():
            if subscribes[key]:
                inline_kb_full.add(InlineKeyboardButton(key, callback_data='subs_'+key+flag))
        return inline_kb_full