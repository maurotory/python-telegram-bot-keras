import logging
import os
import random
import sys
import telegram
from telegram import user
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from tfCalcs import calcAnswer


load_dotenv()

# configurar Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s,"
)
logger = logging.getLogger()


# Solicitar TOKEN

TOKEN = os.getenv("BOT_TOKEN")
mode = os.getenv("BOT_MODE")


if mode == "dev":
    def run(updater):
        # funcion en la que vamos pidiendo a telegram si hemos recivido un mensaje
        updater.start_polling()
        print("BOT CARGADO")
        updater.idle()

elif mode == "prod":
    def run(updater):
        # Acceso HEROKU (producción), en este caso estamos a la escucha de mensajes
        APP_NAME = os.getenv("BOT_APP_NAME")
        PORT = 8443
        print("LISTENING IN URL: ")
        print(f"https://{APP_NAME}:{PORT}/{TOKEN}")
        updater.start_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                key='private.key',
                cert='cert.pem',
                webhook_url=f"https://{APP_NAME}:{PORT}/{TOKEN}"
                )
else:
    logger.info("No se especificó el MODE.")
    sys.exit()


def start(update, context):
    logger.info(
        f"El usuario {update.effective_user['username']}, ha iniciado una conversación")
    name = update.effective_user['first_name']
    update.message.reply_text(f"Hola {name} yo soy tu bot.")



def reply_message(update, context):
    user_id = update.effective_user['id']
    logger.info(f"El usuarioi {user_id} ha enviado un mensaje de texto")
    question = update.message.text
    answer = calcAnswer(question) + ""
    print(answer)
    context.bot.sendMessage(
        chat_id=user_id, text=answer)


if __name__ == "__main__":
    bot = telegram.Bot(token=TOKEN)
    print(bot.getMe())

    # Enlazamos nuestro updater
    updater = Updater(bot.token, use_context=True)

    # Creamos un despachador
    dp = updater.dispatcher

    # Creamos los manejadores
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, reply_message))

    run(updater)
