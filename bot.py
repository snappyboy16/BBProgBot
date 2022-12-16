from aiogram.utils import executor
from start_bot import dp
from handlers import main

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)