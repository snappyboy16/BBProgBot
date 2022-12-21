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

with open(r'C:\Users\iamfi\DataspellProjects\BBProgBot\pkl\model5.pkl', "rb") as f:
    model = pickle.load(f)

tokenizer = RegexpTokenizer(r'\w+')
morph = pymorphy2.MorphAnalyzer()
tfidfconverter = TfidfVectorizer()

data = pd.read_csv(r'C:\Users\iamfi\DataspellProjects\BBProgBot\handlers\translated_data2.csv')
X_train = tfidfconverter.fit_transform(data["utterance"]).toarray()


@dp.message_handler(state='*', commands=['start'])
async def start(message: types.Message):
    await bot.send_message(message.from_user.id, f"👋 Здравствуйте, <b>{message.from_user.first_name}</b>, я - бот, "
                                                 f"созданный, чтобы помогать вам с вашими <b>вопросами</b>.\n\n"
                                                 f"🤖 <b>Бот</b> умеет отвечать на <b>вопросы</b>, связанные с <b>темами</b>:\n\n"
                                                 f"🔹 <em>Создание, удаление, редактирование</em>\n"
                                                 f"🔹 <em>Смена аккаунта, восстановление, изменение пароля</em>\n"
                                                 f"🔹 <em>Проверка оплаты, связь с тех-поддержкой и оператором, опции и сроки</em>\n"
                                                 f"🔹 <em>Доставки, жалоба, отзыв, проверка счета, получение чека</em>\n"
                                                 f"🔹 <em>Отмена, отслеживание, размещение заказа, способы и проблемы с оплатой</em>\n"
                                                 f"🔹 <em>Возврат, адрес доставки</em>\n\n"
                                                 f"🆘 Введите /help , чтобы узнать <b>функционал</b> бота.\n\n"
                                                 f"❗️ Чтобы использовать <b>новый режим</b>, вы должны <b>войти</b> в аккаунт.",
                           reply_markup=kb.main_klava, parse_mode='HTML')
    config.operators = await db.get_all_operators()
    await NotLogin.state_.set()


@dp.message_handler(state='*', commands=['help'])
async def help_me(message: types.Message):
    await bot.send_message(message.from_user.id, f"📜 <b>Список команд:</b>\n\n"
                                                 f"/login — Команда входа в свой аккаунт.\n"
                                                 f"/logout — Команда выхода из своего аккаунта.\n"
                                                 f"/stop — Команда <b>остановки общения</b> с с оператором",
                           parse_mode='HTML')


@dp.callback_query_handler(lambda call: call.data == 'cancel_button', state=InChat.state_)
async def del_queue(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    if callback.from_user.id in config.operators:
        await LoginOperator.state_.set()
    else:
        await LoginUser.state_.set()
    await bot.answer_callback_query(callback.id)
    await db.delete_queue(callback.from_user.id)
    await bot.send_message(callback.from_user.id, '🚫 Поиск <b>остановлен</b>.', parse_mode='HTML')


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
                await bot.send_message(message.from_user.id, "🔍 Начался автоматический поиск нового собеседника.",
                                       reply_markup=kb.cancel_search)
            else:
                await LoginUser.state_.set()
                await bot.send_message(chat_info[1], "🔍 Начался атоматический поиск нового собеседника.",
                                       reply_markup=kb.cancel_search)

            await bot.send_message(chat_info[1], "❗️ Собеседник <b>покинул чат</b>",
                                   reply_markup=types.ReplyKeyboardRemove(),
                                   parse_mode='HTML')
            await bot.send_message(message.from_user.id, "❗️ Вы <b>вышли из чата</b>",
                                   reply_markup=types.ReplyKeyboardRemove(),
                                   parse_mode='HTML')
    except Exception as ex_:
        await bot.send_message(message.from_user.id, "⚠️ Вы <b>не начали</b> чат.", parse_mode='HTML')


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
        res = model.predict(tfidfconverter.transform(
            [' '.join([morph.parse(word)[0][2] for word in tokenizer.tokenize(f'{request}')])]).toarray())
        await message.answer(res[0], reply_markup=kb.bot_pomog)
    except Exception as ex_:
        print(ex_)


@dp.callback_query_handler(lambda call: call.data == 'pomog', state=LoginUser.state_)
async def del_queue(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    await bot.send_message(callback.from_user.id, '❤️ Спасибо, что пользуетесь нашими услугами!\n\n'
                                                  'Не забудьте посетить социальные сети :)\n',
                           reply_markup=kb.ssilka)
    await state.finish()
    await bot.send_message(callback.from_user.id, 'Чтобы воспользоваться новым режимом снова, авторизуйтесь')
    await NotLogin.state_.set()


@dp.callback_query_handler(lambda call: call.data == 'not_pomog', state=LoginUser.state_)
async def helpp(callback: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback.id)
    chat_two = await db.get_chat(callback.from_user.id)
    if await db.create_chat(callback.from_user.id, chat_two) == False:
        await db.add_queue(callback.from_user.id)
        await bot.send_message(callback.from_user.id, f"🔎 Поиск <b>доступного</b> оператора...",
                               reply_markup=kb.cancel_search,
                               parse_mode='HTML')
        await state.finish()
        await InChat.state_.set()
    else:
        await state.finish()
        await InChat.state_.set()
        await bot.send_message(chat_two, "✅ Клиент <b>найден</b>!\n", reply_markup=kb.stop, parse_mode='HTML')
        await bot.send_message(callback.from_user.id, "✅ Оператор <b>найден!</b>\n"
                                                      "Начинайте общение.", parse_mode='HTML', reply_markup=kb.stop)


@dp.message_handler(state=LoginOperator.state_, commands=["find"])
async def find(message: types.Message, state: FSMContext):
    chat_two = await db.get_chat(message.chat.id)
    if await db.create_chat(message.chat.id, chat_two) == False:
        await db.add_queue(message.from_user.id)
        await bot.send_message(message.chat.id, f"🔎 Поиск <b>доступного</b> клиента...", reply_markup=kb.cancel_search,
                               parse_mode='HTML')
        await state.finish()
        await InChat.state_.set()
    else:
        await state.finish()
        await InChat.state_.set()
        await bot.send_message(message.chat.id, "✅ Клиент <b>найден!</b>", reply_markup=kb.stop,
                               parse_mode='HTML')
        await bot.send_message(chat_two, "✅ Оператор <b>найден!</b>", reply_markup=kb.stop,
                               parse_mode='HTML')


@dp.message_handler(state=NotLogin.state_, commands=["login"])
async def login(message: types.Message, state: FSMContext):
    await state.finish()
    if message.from_user.id in config.operators:
        await LoginOperator.state_.set()
        await message.answer('✅ Вы зарегистрировались как оператор.', reply_markup=kb.find)
    elif message.from_user.id in config.admins:
        await LoginAdmin.state_.set()
        await message.answer('✅ Вы зарегистрировались как админ.\n\n'
                             '/add <id пользователя> - Добавление опрератора.\n'
                             '/remove <id пользователя> - Удаление опрератора.')
    else:
        await LoginUser.state_.set()
        await message.answer('✅ Вы зарегистрировались как клиент.\n\n'
                             'Теперь вы можете изложить интересующий вас вопрос.')


@dp.message_handler(state=LoginOperator.state_, commands=["logout"])
async def logout(message: types.Message, state: FSMContext):
    await state.finish()
    await NotLogin.state_.set()
    await message.answer('⚠️ Вы вышли из своего аккаунта.')


@dp.message_handler(state=LoginAdmin.state_, commands=["logout"])
async def logout(message: types.Message, state: FSMContext):
    await state.finish()
    await NotLogin.state_.set()
    await message.answer('⚠️ Вы вышли из своего аккаунта.')


@dp.message_handler(state=LoginUser.state_, commands=["logout"])
async def logout(message: types.Message, state: FSMContext):
    await state.finish()
    await NotLogin.state_.set()
    await message.answer('⚠️ Вы вышли из своего аккаунта.')


@dp.message_handler(state=LoginAdmin.state_, commands=["add"])
async def logout(message: types.Message):
    chat_id = message.text.split()[1]
    if chat_id in config.operators:
        await message.reply('⚠️ Оператор с таким id уже есть в базе.')
    else:
        config.operators.append(chat_id)
        await db.add_operator(chat_id)
        await message.answer('✅ Вы успешно добавили нового оператора.')


@dp.message_handler(state=LoginAdmin.state_, commands=["remove"])
async def logout(message: types.Message):
    chat_id = message.text.split()[1]

    if chat_id in config.operators:
        config.operators.remove(chat_id)
        await db.del_operator(chat_id)
        await message.answer('✅ Вы успешно удалили оператора.')
    else:
        await message.reply('⚠️ Оператора с таким id нет в базе.')


@dp.callback_query_handler(lambda call: call.data == 'old_button', state='*')
async def del_queue(callback: types.CallbackQuery):
    await bot.send_message(callback.from_user.id, '✅Включён старый режим.\n\nВопрос по какой теме вас интересует?',
                           reply_markup=kb.old)


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('key_'), state='*')
async def process_callback_btn_delete(callback_query: types.CallbackQuery):
    if callback_query.data.split('key_')[1] == 'account':
        await bot.send_message(callback_query.from_user.id, text='👤 Проблемы с <b>аккаунтом</b> ⁉️',
                               reply_markup=kb.accounts, parse_mode='HTML')
    if callback_query.data.split('key_')[1] == 'contact':
        await bot.send_message(callback_query.from_user.id, text='📞 Наши <b>контакты</b>',
                               reply_markup=kb.contacts, parse_mode='HTML')
    if callback_query.data.split('key_')[1] == 'deliver':
        await bot.send_message(callback_query.from_user.id, text='🚚 Проблемы с <b>доставкой</b> ⁉️',
                               reply_markup=kb.delivers, parse_mode='HTML')
    if callback_query.data.split('key_')[1] == 'feedback':
        await bot.send_message(callback_query.from_user.id, text='🧑‍💻 <b>Обратную связь</b> можно осуществить ниже',
                               reply_markup=kb.feedbacks, parse_mode='HTML')
    if callback_query.data.split('key_')[1] == 'check':
        await bot.send_message(callback_query.from_user.id, text='📃 Всё о <b>чеках</b>',
                               reply_markup=kb.checks, parse_mode='HTML')
    if callback_query.data.split('key_')[1] == 'order':
        await bot.send_message(callback_query.from_user.id, text='📦 Всё о <b>заказах</b>',
                               reply_markup=kb.orders, parse_mode='HTML')
    if callback_query.data.split('key_')[1] == 'payment':
        await bot.send_message(callback_query.from_user.id, text='💳 Всё об <b>оплате</b>',
                               reply_markup=kb.payments, parse_mode='HTML')
    if callback_query.data.split('key_')[1] == 'refund':
        await bot.send_message(callback_query.from_user.id, text='💸 Всё о <b>возвратах</b>',
                               reply_markup=kb.refunds, parse_mode='HTML')


@dp.callback_query_handler(lambda call: call.data and call.data.startswith('btn_'), state='*')
async def process_callback_btn_delete(callback_query: types.CallbackQuery):
    if callback_query.data.split('btn_')[1] == 'create':
        await bot.send_message(callback_query.from_user.id, text='➕ Чтобы <b>создать аккаунт</b>, <b>создайте '
                                                                 'аккаунт</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'delete':
        await bot.send_message(callback_query.from_user.id,
                               text='❌ Чтобы <b>удалить аккаунт</b>, <b>удалите аккаунт</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'edit':
        await bot.send_message(callback_query.from_user.id,
                               text='✏️ Чтобы <b>редактировать аккаунт</b>, <b>редактируйте аккаунт</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'recover':
        await bot.send_message(callback_query.from_user.id,
                               text='🔐 Чтобы <b>восстановить пароль</b>, <b>восстановите пароль</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'switch':
        await bot.send_message(callback_query.from_user.id,
                               text='🔄 Чтобы <b>сменить аккаунт</b>, <b>смените аккаунт</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'support':
        await bot.send_message(callback_query.from_user.id,
                               text='🛠 Чтобы <b>обратиться в тех.поддержку</b>, <b>обратитесь</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'human':
        await bot.send_message(callback_query.from_user.id,
                               text='🧑‍💻 Чтобы <b>обратиться к оператору</b>, <b>обратитесь</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'options':
        await bot.send_message(callback_query.from_user.id, text='🚚 <b>Варианты доставки</b> следующие:',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'period':
        await bot.send_message(callback_query.from_user.id, text='📅 <b>Сроки доставки</b> следующие:',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'complaint':
        await bot.send_message(callback_query.from_user.id, text='📔 <b>Жалобу</b> можно оформить так:',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'review':
        await bot.send_message(callback_query.from_user.id, text='📚 <b>Отзыв</b> можно оформить так:',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'get':
        await bot.send_message(callback_query.from_user.id,
                               text='📃 Чтобы <b>получить</b> чек заказа, <b>получите его</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'cancel':
        await bot.send_message(callback_query.from_user.id, text='❌ Чтобы <b>отменить заказ</b>, <b>отмените его</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'place':
        await bot.send_message(callback_query.from_user.id,
                               text='📝 Чтобы <b>разместить объявление</b>, <b>разместите его</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'track0':
        await bot.send_message(callback_query.from_user.id, text='👁 Чтобы <b>отследить заказ</b>, <b>отследите его</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'method':
        await bot.send_message(callback_query.from_user.id, text='💳 Доступные <b>способы</b> оплаты:',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'issue':
        await bot.send_message(callback_query.from_user.id, text='📚 Возможные <b>решения проблемы</b>',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'policy':
        await bot.send_message(callback_query.from_user.id, text='📜 Политика <b>возвратов</b> такова',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'got':
        await bot.send_message(callback_query.from_user.id, text='💸 Чтобы <b>оформить возврат</b> нужно',
                               parse_mode='HTML')
    if callback_query.data.split('btn_')[1] == 'track1':
        await bot.send_message(callback_query.from_user.id, text='👁 Чтобы <b>отследить возврат</b> нужно',
                               parse_mode='HTML')


def register_handlers_main(dp: Dispatcher):
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(help_me, commands=['help'])
    dp.register_message_handler(helpp, text='help')
    dp.register_message_handler(del_queue, text='cancel_button')
    dp.register_message_handler(stop, commands=['stop'])
    dp.register_message_handler(login, commands=['login'])
    dp.register_message_handler(logout, commands=['logout'])
    dp.register_message_handler(find, commands=['find'])
