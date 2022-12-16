import aiosqlite


async def add_id(id):
    """Добавляем id пользователя в БД"""
    async with aiosqlite.connect('users_id.db') as db:
        await db.execute(f"""INSERT INTO all_id (user_id) VAlUES({id})""")
        await db.commit()


async def add_queue(chat_id):
    """Добавляем chat_id пользователя в БД"""
    async with aiosqlite.connect(r'database/users_id.db') as db:
        await db.execute(f"""INSERT INTO queue (`chat_id`) VAlUES({chat_id})""")
        await db.commit()


async def delete_queue(chat_id):
    """Добавляем chat_id пользователя в БД"""
    async with aiosqlite.connect(r'database/users_id.db') as db:
        await db.execute(f"""DELETE FROM queue WHERE chat_id = {chat_id}""")
        await db.commit()


async def delete_chat(id_chat):
    """Добавляем chat_id пользователя в БД"""
    async with aiosqlite.connect(r'database/users_id.db') as db:
        await db.execute(f"""DELETE FROM chats WHERE id = {id_chat}""")
        await db.commit()


async def get_chat():
    """Добавляем chat_id пользователя в БД"""
    async with aiosqlite.connect(r'database/users_id.db') as db:
        res = await db.execute(f"""SELECT * FROM queue""", ())
        rows = await res.fetchmany(1)
        if bool(len(rows)):
            for row in rows:
                return row[1]
        else:
            return False


async def get_active_chat(chat_id):
    '''ВНИМАНИЕ!!! КОСТЫЛЬНЫЙ КОД!'''
    async with aiosqlite.connect(r'database/users_id.db') as db:
        chat = await db.execute(f"""SELECT * FROM chats WHERE chat1 = {chat_id}""", ())
        chat = await chat.fetchall()
        id_chat = 0
        for row in chat:
            id_chat = row[0]
            chat_info = [row[0], row[2]]
        if id_chat == 0:
            chat = await db.execute(f"""SELECT * FROM chats WHERE chat2 = {chat_id}""", ())
            chat = await chat.fetchall()
            for row in chat:
                id_chat = row[0]
                chat_info = [row[0], row[1]]
            if chat_id == 0:
                return False
            else:
                return chat_info
        else:
            return chat_info




async def create_chat(one, two):
    """Добавляем chat_id пользователя в БД"""
    async with aiosqlite.connect(r'database/users_id.db') as db:
        if two != False:
            # Создание чата
            await db.execute(f"""DELETE FROM queue WHERE chat_id = {two}""")
            await db.execute(f"""INSERT INTO chats (chat1, chat2) VAlUES({one}, {two})""")
            await db.commit()
            return True
        else:
            # Становимся в очередь
            return False


