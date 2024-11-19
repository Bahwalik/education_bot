import sqlite3
import random

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

def create_questions_bd():
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Questions(
        group_id INTEGER,
        question_id integer PRIMARY KEY,
        question TEXT,
        correct_answer INTEGER
        )
    ''')
    connection.commit()
    connection.close()

from docx import Document

def parse_and_store_questions(filename, group_id):

    # Подключение к базе данных
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    # Чтение документа
    doc = Document(filename)
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    # Переменные для хранения текущих данных
    current_question = None
    current_correct_answer = None
    i = 0
    while i < len(lines):
        if '+ans' in lines[i]:
            i += 1
            current_correct_answer = lines[i]

            cursor.execute("SELECT MAX(question_id) FROM questions")
            max_id = cursor.fetchone()[0]

            if max_id is None:
                next_id = 1
            else:
                next_id = max_id + 1
            current_question = 'question/' + str(next_id)+'.png'
            cursor.execute('INSERT INTO Questions (group_id, question_id, question, correct_answer) VALUES (?, ?, ?, ?)', (1, next_id, current_question, current_correct_answer))
            connection.commit()
        i += 1
    connection.commit()
    connection.close()

def give_question(message):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    cursor.execute("SELECT question_id FROM questions")
    question_ids = cursor.fetchall()

    question_ids = [item[0] for item in question_ids]

    random_question_id = random.choice(question_ids)

    connection.commit()

    cursor.execute("SELECT question, correct_answer FROM questions WHERE question_id = ?", (random_question_id,))
    result = cursor.fetchone()

    question, current_correct_answer = result
    print(random_question_id, message.chat.id)
    cursor.execute('UPDATE Users SET question_id = ? WHERE id = ?', (random_question_id, message.chat.id ))
    connection.commit()
    connection.close()
    return question, current_correct_answer


def check_answer(message, bot, answer):
    text = message.text

    if str(answer) != text:
        bot.send_message(message.chat.id, 'Неверно')
    else:
        bot.send_message(message.chat.id, 'Ответ верный!')
