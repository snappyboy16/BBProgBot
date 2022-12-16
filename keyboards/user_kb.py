from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton

cancel = InlineKeyboardMarkup(resize_keyboard=True)
cancel_button = InlineKeyboardButton('Остановить поиск.', callback_data='cancel_button')
cancel.add(cancel_button)

stop = InlineKeyboardMarkup(resize_keyboard=True)
stop_button = InlineKeyboardButton('Выйти из чата.', callback_data='stop_button')
stop.add(stop_button)