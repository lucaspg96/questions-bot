from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot_token = ""
bot_name = ""
lecture_name = ""
presenter_name = ""

default_message = """
Olá! Sou o {}. Estou aqui para registrar perguntas para a palestra:
<b>{}</b>,
apresentada por <b>{}</b>.
Para enviar uma pergunta, entre /question .
""".format(bot_name, lecture_name, presenter_name)

count = 0

def start(bot,update):
	update.message.reply_text(default_message, parse_mode=ParseMode.HTML)


def question_entry_point(bot,update):
	update.message.reply_text("Por favor, entre sua pergunta ou digite /cancel para cancelar")
	return "WAITING_QUESTION"

def store_question(bot,update):
	text = update.message.text
	if text != None:
		print("Has text")
	else:
		print("Has no text")
	return ConversationHandler.END

def cancel(bot,update):
	update.message.reply_text("Pergunta descartada")
	return ConversationHandler.END

################

updater = Updater(bot_token)

dp = updater.dispatcher


conversation = ConversationHandler(
	entry_points=[CommandHandler("question",question_entry_point)],
	states={
		"WAITING_QUESTION": [MessageHandler(Filters.all,store_question)]
	},
	fallbacks=[CommandHandler('cancel', cancel)]
)

dp.add_handler(conversation)

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text, start))

updater.start_polling()
updater.idle()
