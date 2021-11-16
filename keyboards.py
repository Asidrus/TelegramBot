from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class btnMessage():
    
    inline_bt_subscr_all = InlineKeyboardButton("Все", callback_data='subscr_all_users')
    inline_bt_subscr_test = InlineKeyboardButton("Тесты", callback_data='subscr_test')
    inline_bt_subscr_debug = InlineKeyboardButton("Дебаг", callback_data='subscr_debug')

    async def addKeybrd(self, kb):
        inline_kb_full = InlineKeyboardMarkup(row_width=2)
        for i in kb:
            if kb=='from_users':
                inline_kb_full.add(self.inline_bt_subscr_all)
            if kb == 'debug':
                inline_kb_full.add(self.inline_bt_subscr_debug)
            if kb == 'result_tests':
                inline_kb_full.add(self.inline_bt_subscr_test)

        return inline_kb_full