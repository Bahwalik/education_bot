import sqlite3


def create_new_user(user_id, username):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    # Проверка, существует ли пользователь
    existing_user = check_user(user_id)
    if existing_user:
        print("Пользователь уже существует.")
    else:
        cursor.execute('INSERT INTO Users (id, username) VALUES (?, ?)', (user_id, username))
        connection.commit()
        print(f"Пользователь {username} добавлен с ID {user_id}.")

    connection.close()


def check_user(user_id):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,))
    existing_user = cursor.fetchone()
    connection.close()
    return existing_user


def add_userinfo(user_id, message):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('UPDATE Users SET username = ? WHERE id = ?', (message, user_id))
    connection.commit()
    connection.close()


def process_new_name(message, bot):
    new_name = message.text
    add_userinfo(message.from_user.id, new_name)
    bot.send_message(message.chat.id, 'ФИО изменено')



def create_user_bd():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    username TEXT
    )
    ''')
    connection.commit()
    connection.close()
