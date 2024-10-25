import telebot
from telebot import types
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

with open("user_messages.json", "r") as user_messages_file:
    user_messages = json.load(user_messages_file)

bot = telebot.TeleBot(config["API_token"])

def is_admin(user_id):
    if user_id in config["admins"]:
        return 1
    else:
        return 0

def save_user_message(message):
    try:
        with open("user_messages.json", "w") as f:
            json.dump(message, f, indent=4)
    except Exception as e:
        print(f"Ошибка при сохранении данных пользователя: {str(e)}")


@bot.message_handler(commands=["start"])
def start_message(message):
    bot.send_message(message.chat.id, "Приветсвую! Напишите мне свою просьбу/вопрос/предложение, и я отправлю его администрации!")
    bot.send_message(message.chat.id,"С прочей информацией вы можете ознакомиться с помощью команды /help ")

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if is_admin(message.chat.id):
        bot.send_message(message.chat.id, "Вы успешно авторизовались в админ-панель!")


# @bot.message_handler(func=lambda message=True)
# def handle_message(message):
#     user_message[] =


bot.infinity_polling()