from aiogram.utils import executor
from start_bot import dp
from handlers import main

main.register_handlers_main(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)