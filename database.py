import sqlite3
import random
import telebot

N = 5


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
            current_question = 'question/' + str(next_id) + '.png'
            cursor.execute(
                'INSERT INTO Questions (group_id, question_id, question, correct_answer) VALUES (?, ?, ?, ?)',
                (1, next_id, current_question, current_correct_answer))
            connection.commit()
        i += 1
    connection.commit()
    connection.close()


def check_in_progress(message, bot):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    cursor.execute("SELECT in_progress FROM Users WHERE id = ?", (message.chat.id,))
    check = cursor.fetchone()
    if not check[0]:
        cursor.execute('Update Users SET in_progress = ? WHERE id = ?', (1, message.chat.id))
        bot.send_message(message.chat.id, 'Тестирование начато.')
        cursor.execute('UPDATE Users SET points = 0 WHERE id = ?', (message.chat.id,))
        connection.commit()
        connection.close()
        generate_id_question(message)


def generate_id_question(message):
    str_quest = ''
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute("SELECT question_id FROM questions")
    question_ids = cursor.fetchall()
    question_ids = [item[0] for item in question_ids]
    random_question_ids = random.sample(question_ids, N)
    for i in random_question_ids:
        str_quest += str(i) + '/'
    cursor.execute('UPDATE Users SET question_id = ? WHERE id = ?', (str_quest, message.chat.id))
    connection.commit()
    connection.close()


def give_question(message):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT question_id FROM Users WHERE id = ?', (message.chat.id,))
    result = cursor.fetchone()
    print(result)
    ids_str = str(result[0])
    ids_list = ids_str.split('/')
    ids_list = [id for id in ids_list if id]
    first_id = ids_list[0]
    updated_ids_str = '/'.join(ids_list)

    cursor.execute("SELECT question, correct_answer FROM questions WHERE question_id = ?", (first_id,))
    result = cursor.fetchone()

    question, current_correct_answer = result

    connection.commit()
    connection.close()
    return question, current_correct_answer


def check_passed(message):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    cursor.execute('SELECT passed FROM Users WHERE id = ?', (message.chat.id, ))
    result = cursor.fetchone()
    connection.commit()
    connection.close()
    return result[0]


def start_testing(message, bot):
    if not check_passed(message):
        check_in_progress(message, bot)
        question, answer = give_question(message)
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        button1 = telebot.types.KeyboardButton("1")
        button2 = telebot.types.KeyboardButton("2")
        button3 = telebot.types.KeyboardButton("3")
        button4 = telebot.types.KeyboardButton("4")

        markup.add(button1, button2, button3, button4)
        with open(question, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption='Держи вопрос!', reply_markup=markup)
        bot.register_next_step_handler(message, check_answer, bot, answer)
    else:
        bot.send_message(message.chat.id,'Вы уже успешно сдали тест.')


def print_result(message, bot):
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT points FROM Users WHERE id = ?', (message.chat.id,))
    result = cursor.fetchone()

    if result[0] > N * 0.75:
        bot.send_message(message.chat.id, 'Тест сдан! Поздравляю')
        cursor.execute('UPDATE Users SET passed = 1 WHERE id = ?', (message.chat.id, ))
        connection.commit()
    else:
        bot.send_message(message.chat.id, 'Тест не сдан. Попробуйте еще раз!')
    bot.send_message(message.chat.id, 'Вы набрали ' + str(result[0]) + ' балла(-ов).')
    connection.close()


def check_answer(message, bot, answer):
    text = message.text
    connection = sqlite3.connect('my_database.db')
    cursor = connection.cursor()

    if str(answer) == text:
        cursor.execute('UPDATE Users SET points = points + 1 WHERE id = ?', (message.chat.id,))

    cursor.execute('SELECT question_id FROM Users WHERE id = ?', (message.chat.id,))
    result = cursor.fetchone()

    ids_str = str(result[0])

    ids_list = ids_str.split('/')
    ids_list = [id for id in ids_list if id]
    first_id = ids_list.pop(0)
    updated_ids_str = '/'.join(ids_list)
    cursor.execute('UPDATE Users SET question_id = ? WHERE id = ?', (updated_ids_str, message.chat.id))
    connection.commit()
    if updated_ids_str != '':
        start_testing(message, bot)
    else:
        cursor.execute('UPDATE Users SET in_progress = ? WHERE id = ?', (0, message.chat.id))
        bot.send_message(message.chat.id, 'Тестирование окончено!')
        connection.commit()
        connection.close()
        print_result(message, bot)