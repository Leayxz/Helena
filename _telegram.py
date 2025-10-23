import telebot
from decouple import config

def enviarMensagem(mensagem):
    bot = telebot.TeleBot(str(config("TOKEN_TELEGRAM")))

    try:
        bot.send_message(config("ID_TELEGRAM"), f"{mensagem}")

    except Exception as erro:
        print(f"Algo Errado Com o Telegram!")
