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
        json.dump(tickets, file, indent=4)


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    if user_id not in config["admins"]:
        if user_id not in tickets or not tickets[user_id]["status"]:
            tickets[user_id] = {"status": True, "admin": None}
            save_ticket()
            bot.reply_to(message, "Ваш запрос отправлен. Ожадайте ответа администратора.")
            for admins in config["admins"]:
                bot.send_message(admins, f"Открыт новый тикет от {username}\nid: {user_id}.\nЧтобы подключиться к чату, используйте команду /connect {user_id}")
        elif tickets[user_id]["admin"] in config["admins"]:
            connected_admin = tickets[user_id]["admin"]
            bot.send_message(connected_admin, message.text)
        else:
            bot.reply_to(message, "Ваш запрос отправлен. Ожадайте ответа администратора.")


@bot.message_handler(commands=["connect"])
def connect_to_ticket(message):
    if message.from_user.id not in config["admins"]:
        bot.reply_to(message, "Вы не обладаете правами администратора.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id in tickets and tickets[user_id]["status"] and tickets[user_id]["admin"] == None:
            tickets[user_id] = {"status": True, "admin": message.from_user.id}
            save_ticket()
            bot.send_message(message.from_user.id, f"Вы успешно подключены к тикету {user_id}.")
            bot.send_message(user_id, "Вам отвечает Администратор.")
        elif user_id in tickets and tickets[user_id]["admin"] != None:
            bot.send_message(message.from_user.id, f"Другой администратор уже занялся тикетом id: {user_id}.")
        else:
            bot.send_message(message.from_user.id, "Тикет для данного пользователя не найден или уже закрыт.")
    except (IndexError,ValueError):
        bot.send_message(message.from_user.id, "Пожалуйста, укажите корректный id пользователя. Пример: /connect <user_id>")


@bot.message_handler(commands=["close"])
def close_ticket(message):
    if message.from_user.id not in config["admins"]:
        bot.reply_to(message, "Вы не обладаете правами администратора.")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id in tickets and tickets[user_id]["status"] and tickets[user_id]["admin"] == message.from_user.id:
            tickets[user_id] = {"status": False, "admin": None}
            save_ticket()
            bot.send_message(message.from_user.id, f"Тикет пользователя {user_id} закрыт.")
            bot.send_message(user_id,"Спасибо за обращение! Если нужна помощь, напишите сюда снова!")
        else:
            bot.send_message(message.from_user.id, "Тикет для данного пользователя не найден или уже закрыт.")
    except (IndexError, ValueError):
        bot.send_message(message.from_user.id,"Пожалуйста, укажите корректный id пользователя. Пример: /connect <user_id>")


@bot.message_handler(func=lambda message: message.from_user.id in config["admins"] and message.reply_to_message)
def admin_reply_to_user(message):
    try:
        user_id = int(message.reply_to_message.text.split("ID: ")[1].split(")")[0])
        if tickets.get(user_id, {}).get("admin") == message.from_user.id:
            bot.send_message(user_id,message.text)
    except (IndexError, ValueError):
        bot.send_message(message.from_user.id, "Ошибка при отправке сообщения. Проверьте правильность id пользователя.")

# там str кофликтит с int

bot.infinity_polling()