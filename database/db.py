import aiosqlite


async def add_id(id):
    """Добавляем id пользователя в БД"""
    async with aiosqlite.connect('users_id.db') as db:
        await db.execute(f"""INSERT INTO all_id (user_id) VAlUES({id})""")
        await db.commit()


async def add_queue(chat_id):
    """Добавляем chat_id пользователя в БД"""
    async with aiosqlite.connect('users_id.db') as db:
        await db.execute(f"""INSERT INTO queue (`chat_id`) VAlUES({chat_id})""")
        await db.commit()


async def delete_queue(chat_id):
    """Добавляем chat_id пользователя в БД"""
    async with aiosqlite.connect(r'users_id.db') as db:
        await db.execute(f"""DELETE FROM queue (`chat_id`) ({chat_id})""")
        await db.commit()
