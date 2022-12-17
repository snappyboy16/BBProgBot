from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import config
from database import db
from start_bot import dp, bot
from keyboards import user_kb, operator_kb


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f"Здравствуйте, {message.from_user.first_name}, я - бот, "
                         f"созданный, чтобы помогать вам с вашими вопросами.")


@dp.message_handler(commands=["help"])
async def start(message: types.Message):
    chat_two = await db.get_chat(message.chat.id)
    if await db.create_chat(message.chat.id, chat_two) == False:
        await db.add_queue(message.from_user.id)
        if message.chat.id in config.admins:
            await bot.send_message(message.chat.id, f"Поиск доступного клиента...", reply_markup=user_kb.cancel)
        else:
            await bot.send_message(message.chat.id, f"Поиск доступного оператора...", reply_markup=user_kb.cancel)
    else:
        if message.chat.id in config.admins:
            await bot.send_message(message.chat.id, "Клиент найден!", reply_markup=user_kb.stop)
            await bot.send_message(chat_two, "Оператор найден!", reply_markup=user_kb.stop)
        else:
            await bot.send_message(chat_two, "Клиент найден!", reply_markup=user_kb.stop)
            await bot.send_message(message.chat.id, "Оператор найден!", reply_markup=user_kb.stop)


@dp.callback_query_handler(lambda call: call.data == 'cancel_button')
async def del_queue(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await db.delete_queue(callback.from_user.id)
    await bot.send_message(callback.from_user.id, 'Поиск остановлен.')


@dp.message_handler(commands=["stop"])
async def start(message: types.Message):
    try:
        chat_info = await db.get_active_chat(message.from_user.id)
        if chat_info != False:
            await db.delete_chat(chat_info[0])
            await bot.send_message(chat_info[1], "Собеседник покинул чат", reply_markup=types.ReplyKeyboardRemove())
            await bot.send_message(message.from_user.id, "Вы вышли из чата", reply_markup=types.ReplyKeyboardRemove())
    except Exception as ex_:
        await bot.send_message(message.from_user.id, "Вы не начали чат.")


@dp.message_handler()
async def start(message: types.Message):
    get_active_chat = await db.check_active_chat(message.chat.id)
    if get_active_chat != False:
        one = get_active_chat[1]
        two = get_active_chat[2]
        dct = {
            one: two,
            two: one
        }
        my_id = message.from_user.id
        await bot.send_message(dct[str(my_id)], message.text)

    else:
        pass













def register_handlers_main(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(del_queue, text='cancel_button')
    dp.register_message_handler(del_queue, text='stop_button')