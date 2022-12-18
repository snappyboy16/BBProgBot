from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

import config
from database import db
from start_bot import dp, bot
from keyboards import kb
from states.state import LoginOperator, LoginUser, LoginAdmin, InChat, NotLogin

import pickle

from nltk import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pymorphy2
import pandas as pd

with open(r'C:\Users\aleks\PycharmProjects\BBProgBot\pkl\model5.pkl', "rb") as f:
    model = pickle.load(f)

tokenizer = RegexpTokenizer(r'\w+')
morph = pymorphy2.MorphAnalyzer()
tfidfconverter = TfidfVectorizer()

data = pd.read_csv(r'C:\Users\aleks\PycharmProjects\BBProgBot\handlers\translated_data2.csv')
X_train = tfidfconverter.fit_transform(data["utterance"]).toarray()


@dp.message_handler(state='*', commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f"Здравствуйте, {message.from_user.first_name}, я - бот, "
                                                 f"созданный, чтобы помогать вам с вашими вопросами.\n"
                                                 f"Бот умеет отвечать на вопросы, свящанные с данными темами:\n"
                                                 f"Создание, удаление, редактирование и смена аккаунта,"
                                                 f"восстановление, изменение пароля, проверка оплаты "
                                                 f"связь с тех-поддержкой и оператором, опции и сроки "
                                                 f"доставки, жалоба, отзыв, проверка счета, получение чека, "
                                                 f"отмена, отслеживание, размещение заказа, способы и проблемы с оплатой "
                                                 f"возврат, адрес доставки.\n"
                                                 f"Введите /help , чтобы узнать функционал бота.\n"
                                                 f"Чтобы использовать новый режим, вы должны войти в аккаунт.", reply_markup=kb.main_klava)
    config.operators = await db.get_all_operators()
    await NotLogin.state_.set()


@dp.message_handler(state='*', commands=['help'])
async def help_me(message: types.Message):
    await bot.send_message(message.from_user.id, f"Список команд:\n"
                                                 f"/login - Команда входа в свой аккаунт.\n"
                                                 f"/logout - Команда выхода из своего аккаунта./n"
                                                 f"/find - Команда поиска клиента для оператора.\n"
                                                 f"/stop - Команда остановки диалога тет-а-тет.")


@dp.callback_query_handler(lambda call: call.data == 'cancel_button', state=InChat.state_)
async def del_queue(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if callback.from_user.id in config.operators:
        await LoginOperator.state_.set()
    else:
        await LoginUser.state_.set()
    await bot.answer_callback_query(callback.id)
    await db.delete_queue(callback.from_user.id)
    await bot.send_message(callback.from_user.id, 'Поиск остановлен.')


@dp.message_handler(state=InChat.state_, commands=["stop"])
async def stop(message: types.Message, state: FSMContext):
    try:
        chat_info = await db.get_active_chat(message.from_user.id)
        if chat_info != False:
            await db.delete_queue(chat_info[1])
            await db.delete_chat(chat_info[0])
            await state.finish()
            if message.from_user.id in config.operators:
                await LoginOperator.state_.set()
                await bot.send_message(chat_info[1], "Начался автоматический поиск нового собеседника.",
                                       reply_markup=kb.cancel_search)
            else:
                await LoginUser.state_.set()
                await bot.send_message(message.from_user.id, "Начался атоматический поиск нового собеседника.",
                                       reply_markup=kb.cancel_search)

            await bot.send_message(chat_info[1], "Собеседник покинул чат.", reply_markup=types.ReplyKeyboardRemove())
            await bot.send_message(message.from_user.id, "Вы вышли из чата.", reply_markup=types.ReplyKeyboardRemove())
    except Exception as ex_:
        await bot.send_message(message.from_user.id, "Вы не начали чат.")


@dp.message_handler(state=InChat.state_, content_types=['photo', 'text'])
async def start(message: types.Message):
    get_active_chat = await db.check_active_chat(message.chat.id)
    if get_active_chat != False:
        my_id = message.from_user.id
        one = get_active_chat[1]
        two = get_active_chat[2]
        dct = {
            one: two,
            two: one
        }
        if message.text:
            await bot.send_message(dct[str(my_id)], message.text)
        elif message.photo:
            await bot.send_photo(dct[str(my_id)], message.photo[-1].file_id)
        else:
            pass
    else:
        pass


@dp.message_handler(state=LoginUser.state_)
async def start(message: types.Message):
    request = message.text
    try:
        res = model.predict(tfidfconverter.transform([' '.join([morph.parse(word)[0][2] for word in tokenizer.tokenize(f'{request}')])]).toarray())
        await message.answer(res[0], reply_markup=kb.bot_pomog)
    except Exception as ex_:
        print(ex_)


@dp.callback_query_handler(lambda call: call.data == 'pomog', state=LoginUser.state_)
async def del_queue(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, 'Спасибо, что пользуетесь нашими услугами!\n'
                                                  'Не забудьте зайти в наши социальные сети)\n',
                           reply_markup=kb.ssilka)


@dp.callback_query_handler(lambda call: call.data == 'not_pomog', state=LoginUser.state_)
async def helpp(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    chat_two = await db.get_chat(callback.from_user.id)
    if await db.create_chat(callback.from_user.id, chat_two) == False:
        await db.add_queue(callback.from_user.id)
        await bot.send_message(callback.from_user.id, f"Поиск доступного оператора...", reply_markup=kb.cancel_search)
        await state.finish()
        await InChat.state_.set()
    else:
        await state.finish()
        await InChat.state_.set()
        await bot.send_message(chat_two, "Клиент найден!", reply_markup=kb.stop)
        await bot.send_message(callback.from_user.id, "Оператор найден!", reply_markup=kb.stop)


@dp.message_handler(state=LoginOperator.state_, commands=["find"])
async def find(message: types.Message, state: FSMContext):
    chat_two = await db.get_chat(message.chat.id)
    if await db.create_chat(message.chat.id, chat_two) == False:
        await db.add_queue(message.from_user.id)
        await bot.send_message(message.chat.id, f"Поиск клиента...", reply_markup=kb.cancel_search)
        await state.finish()
        await InChat.state_.set()
    else:
        await state.finish()
        await InChat.state_.set()
        await bot.send_message(message.chat.id, "Клиент найден!", reply_markup=kb.stop)
        await bot.send_message(chat_two, "Оператор найден!", reply_markup=kb.stop)


@dp.message_handler(state=NotLogin.state_, commands=["login"])
async def login(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id in config.operators:
        await LoginOperator.state_.set()
        await message.answer('Вы зарегистрировались как оператор.', reply_markup=kb.find)
    elif message.from_user.id in config.admins:
        await LoginAdmin.state_.set()
        await message.answer('Вы зарегистрировались как админ.\n'
                             '/add <id пользователя> - Добавление опрератора.\n'
                             '/remove <id пользователя> - Удаление опрератора.')
    else:
        await LoginUser.state_.set()
        await message.answer('Вы зарегистрировались как клиент.\n'
                             'Теперь вы можете изложить интересующий вас вопрос.')


@dp.message_handler(state=LoginOperator.state_, commands=["logout"])
async def logout(message: types.Message, state: FSMContext):
    await state.finish()
    await NotLogin.state_.set()
    await message.answer('Вы вышли из своего аккаунта.')


@dp.message_handler(state=LoginAdmin.state_, commands=["logout"])
async def logout(message: types.Message, state: FSMContext):
    await state.finish()
    await NotLogin.state_.set()
    await message.answer('Вы вышли из своего аккаунта.')


@dp.message_handler(state=LoginAdmin.state_, commands=["add"])
async def logout(message: types.Message):
    chat_id = message.text.split()[1]
    if chat_id in config.operators:
        await message.reply('Оператор с таким id уже есть в базе.')
    else:
        config.operators.append(chat_id)
        await db.add_operator(chat_id)
        await message.answer('Вы успешно добавили нового оператора.')


@dp.message_handler(state=LoginAdmin.state_, commands=["remove"])
async def logout(message: types.Message):
    chat_id = message.text.split()[1]

    if chat_id in config.operators:
        config.operators.remove(chat_id)
        await db.del_operator(chat_id)
        await message.answer('Вы успешно удалили оператора.')
    else:
        await message.reply('Оператора с таким id нет в базе.')


@dp.callback_query_handler(lambda call: call.data == 'old_button')
async def del_queue(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, 'Включён старый режим.\nВопрос по какой теме вас интересует?', reply_markup=kb.old)


@dp.callback_query_handler(lambda call: call.data == 'new_button')
async def del_queue(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, 'Включён новый режим.\nЗайдите в свой аккаунт командой /login')


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('key_'), state='*')
async def process_callback_btn_delete(callback_query: types.CallbackQuery):
    if callback_query.data.split('key_')[1] == 'account':
        await bot.send_message(callback_query.from_user.id, text='Проблемы с аккаунтом?', reply_markup=kb.accounts)
    if callback_query.data.split('key_')[1] == 'contact':
        await bot.send_message(callback_query.from_user.id, text='Наши контакты', reply_markup=kb.contacts)
    if callback_query.data.split('key_')[1] == 'deliver':
        await bot.send_message(callback_query.from_user.id, text='Проблемы с доставкой?', reply_markup=kb.delivers)
    if callback_query.data.split('key_')[1] == 'feedback':
        await bot.send_message(callback_query.from_user.id, text='Обратную связь можно осуществить ниже', reply_markup=kb.feedbacks)
    if callback_query.data.split('key_')[1] == 'check':
        await bot.send_message(callback_query.from_user.id, text='Всё о чеках', reply_markup=kb.checks)
    if callback_query.data.split('key_')[1] == 'order':
        await bot.send_message(callback_query.from_user.id, text='Всё о заказах', reply_markup=kb.orders)
    if callback_query.data.split('key_')[1] == 'payment':
        await bot.send_message(callback_query.from_user.id, text='Всё об оплате', reply_markup=kb.payments)
    if callback_query.data.split('key_')[1] == 'refund':
        await bot.send_message(callback_query.from_user.id, text='Всё о возвратах', reply_markup=kb.refunds)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('btn_'), state='*')
async def process_callback_btn_delete(callback_query: types.CallbackQuery):
    if callback_query.data.split('btn_')[1] == 'create':
        await bot.send_message(callback_query.from_user.id, text='Чтобы создать аккаунт, создайте аккаунт')
    if callback_query.data.split('btn_')[1] == 'delete':
        await bot.send_message(callback_query.from_user.id, text='Чтобы удалить аккаунт, удалите аккаунт')
    if callback_query.data.split('btn_')[1] == 'edit':
        await bot.send_message(callback_query.from_user.id, text='Чтобы редактировать аккаунт, редактируйте аккаунт')
    if callback_query.data.split('btn_')[1] == 'recover':
        await bot.send_message(callback_query.from_user.id, text='Чтобы восстановить пароль, восстановите пароль')
    if callback_query.data.split('btn_')[1] == 'switch':
        await bot.send_message(callback_query.from_user.id, text='Чтобы сменить аккаунт, смените аккаунт')
    if callback_query.data.split('btn_')[1] == 'support':
        await bot.send_message(callback_query.from_user.id, text='Чтобы обратиться в тех.поддержку, обратитесь')
    if callback_query.data.split('btn_')[1] == 'human':
        await bot.send_message(callback_query.from_user.id, text='Чтобы обратиться к оператору, обратитесь')
    if callback_query.data.split('btn_')[1] == 'options':
        await bot.send_message(callback_query.from_user.id, text='Варианты доставки следующие:')
    if callback_query.data.split('btn_')[1] == 'period':
        await bot.send_message(callback_query.from_user.id, text='Сроки доставки следующие:')
    if callback_query.data.split('btn_')[1] == 'complaint':
        await bot.send_message(callback_query.from_user.id, text='Жалобу можно оформить так:')
    if callback_query.data.split('btn_')[1] == 'review':
        await bot.send_message(callback_query.from_user.id, text='Отзыв можно оформить так:')
    if callback_query.data.split('btn_')[1] == 'get':
        await bot.send_message(callback_query.from_user.id, text='Чтобы получить чек заказа, получите его')
    if callback_query.data.split('btn_')[1] == 'cancel':
        await bot.send_message(callback_query.from_user.id, text='Чтобы отменить заказ, отмените его')
    if callback_query.data.split('btn_')[1] == 'place':
        await bot.send_message(callback_query.from_user.id, text='Чтобы разместить объявление, разместите его')
    if callback_query.data.split('btn_')[1] == 'track0':
        await bot.send_message(callback_query.from_user.id, text='Чтобы отследить заказ, отследите его')
    if callback_query.data.split('btn_')[1] == 'method':
        await bot.send_message(callback_query.from_user.id, text='Доступные способы оплаты:')
    if callback_query.data.split('btn_')[1] == 'issue':
        await bot.send_message(callback_query.from_user.id, text='Возможные решения проблемы')
    if callback_query.data.split('btn_')[1] == 'policy':
        await bot.send_message(callback_query.from_user.id, text='Политика возвратов такова')
    if callback_query.data.split('btn_')[1] == 'got':
        await bot.send_message(callback_query.from_user.id, text='Чтобы оформить возврат нужно')
    if callback_query.data.split('btn_')[1] == 'track1':
        await bot.send_message(callback_query.from_user.id, text='Чтобы отследить возврат нужно')



def register_handlers_main(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(help_me, commands=['help'])
    dp.register_message_handler(helpp, text='help')
    dp.register_message_handler(del_queue, text='cancel_button')
    dp.register_message_handler(stop, commands=['stop'])
    dp.register_message_handler(login, commands=['login'])
    dp.register_message_handler(logout, commands=['logout'])
    dp.register_message_handler(find, commands=['find'])
