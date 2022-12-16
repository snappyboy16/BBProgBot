from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import db
from start_bot import dp, bot
from keyboards import user_kb, operator_kb


@dp.message_handlers(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Ку')


def register_handlers_main(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start'])