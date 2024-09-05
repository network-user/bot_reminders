import sqlite3

connection = sqlite3.connect('telegram_bot_database.db')
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE USERS
    (
    id INTEGER,
    name TEXT,
    items TEXT
    )
''')


connection.close()