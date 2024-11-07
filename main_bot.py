import telebot
from telebot import types
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

with open("tickets.json", "r") as tickets_file:
    tickets = json.load(tickets_file)


bot = telebot.TeleBot(config["API_token"])


def save_ticket():
    with open("tickets.json", "w") as file:
        json.dump(tickets, file)


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name

    if user_id not in tickets or not tickets[user_id]["status"]:
        tickets[user_id] = {"status": True, "admin": None}
        save_ticket()
        bot.reply_to(message, "Ваш запрос отправлен. Ожадайте ответа администратора.")
        for admins in config["adimns"]:
            bot.send_message(admins, f"Открыто новое обращение от {username}\nID: {user_id}.\nЧтобы подключиться к чату, используйте команду /connect {user_id}")
    elif tickets[user_id]["admin"] in config["admins"]:
        connected_admin = tickets[user_id]["admin"]
        bot.send_message(connected_admin, message.text)
    else:
        bot.reply_to(message, "Ваш запрос отправлен. Ожадайте ответа администратора.")


@bot.message_handler(commands=["connect"])
def connect_to_user(message):
    if message.from_user.id not in config["admins"]:
        bot.reply_to(message, "Вы не обладаете правами администратора.")
        return

    try:
        #user_id = int(message.text.split()[1])

bot.infinity_polling()