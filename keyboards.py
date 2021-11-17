from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class btnMessage():
    
    inline_bt_subscr_all = InlineKeyboardButton("Все", callback_data='subscr_all_users')
    inline_bt_subscr_test = InlineKeyboardButton("Тесты", callback_data='subscr_test')
    inline_bt_subscr_debug = InlineKeyboardButton("Дебаг", callback_data='subscr_debug')

    inline_bt_unsubscr_all = InlineKeyboardButton("Все", callback_data='unsubscr_all_users')
    inline_bt_unsubscr_test = InlineKeyboardButton("Тесты", callback_data='unsubscr_test')
    inline_bt_unsubscr_debug = InlineKeyboardButton("Дебаг", callback_data='unsubscr_debug')


    inline_bt_user_tester = InlineKeyboardButton("Тесты", callback_data='user_tester')
    inline_bt_users_all = InlineKeyboardButton("Все", callback_data='users_all')
    inline_kb_changing_user = InlineKeyboardMarkup(row_width=2).row(inline_bt_user_tester,inline_bt_users_all)


    async def addKeybrd(self, kb, key):
        inline_kb_full = InlineKeyboardMarkup(row_width=2)
        if key == 'sub':
            for i in kb:
                if i=='from_users':
                    inline_kb_full.add(self.inline_bt_subscr_all)
                elif i == 'debug':
                    inline_kb_full.add(self.inline_bt_subscr_debug)
                elif i == 'result_tests':
                    inline_kb_full.add(self.inline_bt_subscr_test)
        else:
            for i in kb:
                if i =='from_users':
                    inline_kb_full.add(self.inline_bt_unsubscr_all)
                elif i == 'debug':
                    inline_kb_full.add(self.inline_bt_unsubscr_debug)
                elif i == 'result_tests':
                    inline_kb_full.add(self.inline_bt_unsubscr_test)
        return inline_kb_full