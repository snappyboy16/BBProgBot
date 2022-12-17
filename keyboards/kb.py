from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton

cancel = InlineKeyboardMarkup(resize_keyboard=True)
cancel_button = InlineKeyboardButton('Остановить поиск.', callback_data='cancel_button')
cancel.add(cancel_button)

stop = ReplyKeyboardMarkup(resize_keyboard=True)
stop_button = KeyboardButton('/stop')
stop.add(stop_button)

helpp = InlineKeyboardMarkup(resize_keyboard=True)
helpp_button = InlineKeyboardButton('Перенаправить меня на оператора', callback_data='helpp')
helpp.add(helpp_button)