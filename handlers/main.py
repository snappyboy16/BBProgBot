from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import db
from start_bot import dp, bot
from keyboards import user_kb, operator_kb


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f"Здравствуйте, {message.from_user.first_name}, я - бот, "
                         f"созданный, чтобы помогать вам с вашими вопросами.")



@dp.message_handler(commands=["help"])
async def start(message: types.Message):
    await db.add_queue(message.from_user.id)
    await message.answer(f"Поиск доступного оператора...", reply_markup=user_kb.cancel)


@dp.callback_query_handler(lambda call: call.data == 'cancel_button')
async def del_queue(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await db.delete_queue(callback.from_user.id)
    await bot.send_message(callback.from_user.id, 'Поиск остановлен.')


def register_handlers_main(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(del_queue, text='cancel_button')