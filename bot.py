import logging
import os
import random
import sys
import telegram
from telegram import user
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tfCalcs import calcAnswer

# configurar Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s,"
)
logger = logging.getLogger()


# Solicitar TOKEN


TOKEN = os.getenv("TOKEN")
mode = os.getenv("MODE")
print(mode)

if mode == "dev":
    def run(updater):
        # funcion en la que vamos pidiendo a telegram si hemos recivido un mensaje
        updater.start_polling()
        print("BOT CARGADO")
        updater.idle()

elif mode == "prod":
    def run(updater):
        # Acceso HEROKU (producción), en este caso estamos a la escucha de mensajes
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(
            f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")
else:
    logger.info("No se especificó el MODE.")
    sys.exit()


def start(update, context):
    logger.info(
        f"El usuario {update.effective_user['username']}, ha iniciado una conversación")
    name = update.effective_user['first_name']
    update.message.reply_text(f"Hola {name} yo soy tu bot.")


def random_number(update, context):
    user_id = update.effective_user['id']
    logger.info(f"El usuarioi {user_id} ha solicitado un numero aleatorio")
    number = random.randint(0, 10)
    context.bot.sendMessage(
        chat_id=user_id, text=f"Numero aleatorio:\n{number}")


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
    dp.add_handler(CommandHandler("random", random_number))
    dp.add_handler(MessageHandler(Filters.text, reply_message))

    run(updater)
