import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

with open("tickets.json", "r") as tickets_file:
    tickets = json.load(tickets_file)


bot = telebot.TeleBot(config["API_token"])


def save_ticket():
    with open("tickets.json", "w") as file:
        json.dump(tickets, file, indent=4)


@bot.callback_query_handler(func=lambda call: call.data.startswith("connect_"))
def connect_ticket(call):
    if call.from_user.id not in config["admins"]:
        bot.answer_callback_query(call, "Вы не обладаете правами администратора.")
        return

    user_id = int(call.data.split("_")[1])

    if str(user_id) in tickets and tickets[str(user_id)]["status"] and tickets[str(user_id)]["admin"] == None:
        tickets[str(user_id)]["admin"] = call.from_user.id
        save_ticket()
        bot.send_message(call.from_user.id, f"Вы успешно подключены к тикету {user_id}.")
        bot.send_message(user_id, "Вам отвечает Администратор.")
    elif str(user_id) in tickets and tickets[str(user_id)]["admin"] != None:
        bot.send_message(call.from_user.id, f"Другой администратор уже занялся тикетом id: {user_id}.")

    #     user_id = int(message.text.split()[1])
    #     if str(user_id) in tickets and tickets[str(user_id)]["status"] and tickets[str(user_id)]["admin"] == None:
    #         tickets[str(user_id)] = {"status": True, "admin": message.from_user.id}
    #         save_ticket()
    #         bot.send_message(message.from_user.id, f"Вы успешно подключены к тикету {user_id}.")
    #         bot.send_message(user_id, "Вам отвечает Администратор.")
    #     elif str(user_id) in tickets and tickets[str(user_id)]["admin"] != None:
    #         bot.send_message(message.from_user.id, f"Другой администратор уже занялся тикетом id: {user_id}.")
    #     else:
    #         bot.send_message(message.from_user.id, "Тикет для данного пользователя не найден или уже закрыт.")
    # except (IndexError,ValueError):
    #     bot.send_message(message.from_user.id, "Пожалуйста, укажите корректный id пользователя. Пример: /connect <user_id>")


@bot.message_handler(commands=["close"])
def close_ticket(message):
    if message.from_user.id not in config["admins"]:
        bot.reply_to(message, "Вы не обладаете правами администратора.")
        return

    try:
        user_id = int(message.text.split()[1])
        if str(user_id) in tickets and tickets[str(user_id)]["status"] and tickets[str(user_id)]["admin"] == message.from_user.id:
            tickets[str(user_id)] = {"status": False, "admin": None}
            save_ticket()
            bot.send_message(message.from_user.id, f"Тикет пользователя {user_id} закрыт.")
            bot.send_message(user_id,"Спасибо за обращение! Если нужна помощь, напишите сюда снова!")
        else:
            bot.send_message(message.from_user.id, "Тикет для данного пользователя не найден или уже закрыт.")
    except (IndexError, ValueError):
        bot.send_message(message.from_user.id,"Пожалуйста, укажите корректный id пользователя. Пример: /connect <user_id>")


@bot.message_handler(func=lambda message: message.from_user.id in config["admins"])
def admin_reply_to_user(message):
    admin_id = message.from_user.id
    connected_ticket = None

    for user_id, ticket in tickets.items():
        if ticket["admin"] == admin_id and ticket["status"]:
            connected_ticket = int(user_id)
            break

    if connected_ticket:
        bot.send_message(connected_ticket, message.text)
    else:
        bot.send_message(connected_ticket,"Вы не подключены ни к одному тикету.")


@bot.message_handler(func=lambda message: True)
def handle_user_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    if user_id not in config["admins"]:
        if str(user_id) not in tickets or not tickets[str(user_id)]["status"]:
            tickets[str(user_id)] = {"status": True, "admin": None}
            save_ticket()
            bot.reply_to(message, "Ваш запрос отправлен. Ожадайте ответа администратора.")

            connect_button = InlineKeyboardMarkup()
            connect_button.add(InlineKeyboardButton("Подключиться", callback_data=f"connect_{user_id}"))
            for admins in config["admins"]:
                bot.send_message(admins, f"Открыт новый тикет от {username}\nid: {user_id}.\nОбращение:{message.text}\nЧтобы подключиться к чату, используйте команду /connect {user_id}", reply_markup = connect_button)
        elif tickets[str(user_id)]["admin"] in config["admins"]:
            connected_admin = tickets[str(user_id)]["admin"]
            bot.send_message(connected_admin, message.text)
        else:
            bot.reply_to(message, "Ожадайте ответа администратора.")


bot.infinity_polling()