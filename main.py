import telebot
import database
import parsing

bot = telebot.TeleBot("paste your tg_key", parse_mode=None)
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

@bot.message_handler(commands=['start_testing'])
def handle_rename(message):
    database.start_testing(message, bot)


def register_fio(message):
    user_id = message.from_user.id
    fio = message.text
    database.create_new_user(user_id, fio)


bot.infinity_polling()
