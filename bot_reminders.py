import asyncio

from aiogram import F
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import sqlite3

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

bot = Bot(token="YOU API")

dp = Dispatcher()


class Form(StatesGroup):
    waiting_for_item = State()


async def save_user(message: types.Message):
    user = message.from_user.username
    user_id = message.from_user.id
    with sqlite3.connect("telegram_bot_database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM USERS WHERE name=?", (user,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute('INSERT INTO USERS (name, id) VALUES (?, ?)',
                           (user, user_id,))
            connection.commit()
            print("Пользователь сохранён")
        else:
            print("Пользователь уже существует")
    return 'Новый пользователь: ', user


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    kb = [
        [types.KeyboardButton(text="Добавить вещи")],
        [types.KeyboardButton(text="Посмотреть вещи")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await save_user(message)
    await message.answer("Здравствуйте, этот бот предназначен для напоминаний.", reply_markup=keyboard)


@dp.message(F.text == "Добавить вещи")
async def add_item(message: types.Message, state: FSMContext):
    await message.answer("Введите сообщение для добавления в список:")
    await state.set_state(Form.waiting_for_item)


@dp.message(Command("delete"))
async def cmd_clear_items(message: types.Message):
    with sqlite3.connect("telegram_bot_database.db") as connection:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM USERS')
        connection.commit()
    await message.answer(f"Все требуемые вещи были очищены")


@dp.message(F.text == "Посмотреть вещи")
@dp.message(Command("show_all"))
async def show_all_db(message: types.Message):
    with sqlite3.connect("telegram_bot_database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("""SELECT items FROM users""")
        all_db = cursor.fetchall()
    if all_db:
        all_db_str = ", ".join([str(item[0]) for item in all_db])
        await message.answer(f"Все вещи: {all_db_str}")
    else:
        await message.answer("База данных пуста или данные не были найдены.")


@dp.message(Form.waiting_for_item)
async def process_item(message: types.Message, state: FSMContext):
    item = message.text
    with sqlite3.connect("telegram_bot_database.db") as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO USERS (items) VALUES (?)', (item,))
        connection.commit()
    await message.answer(f"Добавлено: {item}")
    await state.clear()


async def send_messages_all_users(message: types.Message, text: str):
    with sqlite3.connect("telegram_bot_database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM USERS")
        results = cursor.fetchall()
        for row in results:
            user_id = row[0]
            print(text)
            await bot.send_message(user_id, text)


@dp.message(Command("alart_all"))
async def alart_all_users(message: types.Message):
    text = "Тестовое сообщение"
    await send_messages_all_users(message, text)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
