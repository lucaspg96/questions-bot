from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode
from Models import Question
import logging
from datetime import datetime

from pymongo import MongoClient

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

bot_token = ""
bot_name = ""

lecture_name = ""
presenter_name = ""
presenter_id = #integer

default_message = """
Olá! Sou o {}. Estou aqui para registrar perguntas para a palestra:
<b>{}</b>,
apresentada por <b>{}</b>.
Para enviar uma pergunta, entre /question .
""".format(bot_name, lecture_name, presenter_name)

count = MongoClient()["telegram"]["questions"].count()

def start(bot,update):
	update.message.reply_text(default_message, parse_mode=ParseMode.HTML)

def question_entry_point(bot,update):
	update.message.reply_text("Entrando no modo de perguntas. Cada mensagem que enviar será considerado uma pergunta. Digite /done para finalizar")
	return "WAITING_QUESTION"

def store_question(bot,update):
	text = update.message.text

	if text == "/done":
			return done(bot,update)

	if text[0] == "/":
		update.message.reply_text("Enquanto no modo de perguntas, comandos serão desconsiderados, exceto pelo /done")
		return "WAITING_QUESTION"

	if text != None:

		user = update.message.from_user
		question = Question()
		question["text"] = text
		question["user_id"] = user.id
		question["user_name"] = user.first_name + " " + user.last_name
		question["user_tag"] = "@"+user.username if user.username else ""
		question["time"] = datetime.now()

		question.save()

		global count
		count += 1

		update.message.reply_text("Obrigado. Sua mensagem foi adicionada na pilha na posição {}. Fique a vontade para mandar outra pergunta ou entre /done para finalizar."\
			.format(count))

	else:
		update.message.reply_text("Por favor, entre uma pergunta em texto. Outros tipos de mensagens serão desconsiderados")
	
	return "WAITING_QUESTION"
	

def get_oldest_question(bot,update):
	if update.message.from_user.id == presenter_id:
		question = Question.get_oldest()
		print(question)
		if question:
			update.message.reply_text(str(question))
			question.remove()
		else:
			update.message.reply_text("Não existem perguntas a serem respondidas")
	else:
		update.message.reply_text("Perdão, mas você não tem permissão de consultar as perguntas")

def done(bot,update):
	update.message.reply_text("Obrigado!")
	return ConversationHandler.END

################

updater = Updater(bot_token)

dp = updater.dispatcher


conversation = ConversationHandler(
	entry_points=[CommandHandler("question",question_entry_point)],
	states={
		"WAITING_QUESTION": [MessageHandler(Filters.all,store_question)]
	},
	fallbacks=[
		CommandHandler('done', done)
	]
)

dp.add_handler(conversation)

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("questions",get_oldest_question))
dp.add_handler(MessageHandler(Filters.all, start))

updater.start_polling()
updater.idle()
