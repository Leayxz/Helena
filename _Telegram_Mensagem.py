import telebot
from decouple import config

def enviarMensagem(mensagem):
    bot = telebot.TeleBot(config("Token_Telegram"))

    try:
        bot.send_message(config("Id_Telegram"), f"{mensagem}")

    except Exception as erro:
        print(f"Algo Errado Com o Telegram!")
