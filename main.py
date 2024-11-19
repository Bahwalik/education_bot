import telebot
import database
import parsing

bot = telebot.TeleBot("7173651040:AAFStDBOIUNdGPkQ1TpxoAw35drV-Wqtu9g", parse_mode=None)
database.create_user_bd()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if database.check_user(message.from_user.id) is None:
        bot.reply_to(message, "Привет. Отправь свое ФИО")
        bot.register_next_step_handler(message, register_fio)
    else:
        bot.reply_to(message, 'Добро пожаловать, ' + parsing.username(database.check_user(message.from_user.id)[1]))


@bot.message_handler(commands=['rename'])
def handle_rename(message):
    bot.send_message(message.chat.id, "Введите ваше новое ФИО:")
    bot.register_next_step_handler(message, database.process_new_name, bot)  # Передаем bot

@bot.message_handler(commands=['next_question'])
def handle_rename(message):
    bot.send_message(message.chat.id, 'Держи вопрос:')
    question, answer = database.give_question(message)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=4, one_time_keyboard=True)
    button1 = telebot.types.KeyboardButton("1")
    button2 = telebot.types.KeyboardButton("2")
    button3 = telebot.types.KeyboardButton("3")
    button4 = telebot.types.KeyboardButton("4")

    markup.add(button1, button2, button3, button4)
    with open(question, 'rb') as photo:
        bot.send_photo(message.chat.id, photo,caption='Держи вопрос!',reply_markup=markup)
    bot.register_next_step_handler(message, database.check_answer, bot, answer)

def register_fio(message):
    user_id = message.from_user.id
    fio = message.text
    database.create_new_user(user_id, fio)


bot.infinity_polling()
