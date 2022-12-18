from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton

cancel = InlineKeyboardMarkup(resize_keyboard=True)
cancel_button = InlineKeyboardButton('Остановить поиск.', callback_data='cancel_button')
cancel.add(cancel_button)

stop = ReplyKeyboardMarkup(resize_keyboard=True)
stop_button = KeyboardButton('/stop')
stop.add(stop_button)

bot_pomog = InlineKeyboardMarkup(resize_keyboard=True)
pomog = InlineKeyboardButton('Бот помог мне.', callback_data='pomog')
not_pomog = InlineKeyboardButton('Обратиться в поддержку.', callback_data='not_pomog')
bot_pomog.add(pomog, not_pomog)

ssilka = InlineKeyboardMarkup(resize_keyboard=True)
vk_ssilka = InlineKeyboardButton('Наше Вконтакте', url='https://vk.cc/cjOXsu', callback_data='vk')
tg_ssilka = InlineKeyboardButton('Наш Телеграмм', url='https://t.me/rksi_ru', callback_data='tg')
ssilka.add(vk_ssilka, tg_ssilka)