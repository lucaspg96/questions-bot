#telegram imports
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from telegram import ParseMode

#Database model import
from Models import Question

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

#token get from @bothfather
bot_token = ""
#a name to the bot
bot_name = ""

lecture_name = ""
presenter_name = ""

#telegram's id from the presenter. Can be obtained with @userinfobot.
#must be a number, not a string
presenter_id = 0

#get the queue state (the ideal to a presentation is to be 0, since the database should be empty)
count = Question.count()

#function to /start command and not mapped events
def start(bot,update):
	text = """
Olá! Sou o {}. Estou aqui para registrar perguntas para a palestra:
<b>{}</b>,
apresentada por <b>{}</b>.
Para enviar uma pergunta, entre /question .
""".format(bot_name, lecture_name, presenter_name)

	update.message.reply_text(default_message, parse_mode=ParseMode.HTML)

#entry point function to questions mode
def question_entry_point(bot,update):
	update.message.reply_text("Entrando no modo de perguntas. Cada mensagem que enviar será considerado uma pergunta. Digite /done para finalizar")
	return "WAITING_QUESTION"

#function to receive and store a question, if is a valid one
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
	
#funtion to get the oldest question at the database
def get_oldest_question(bot,update):
	if update.message.from_user.id == presenter_id:
		question = Question.get_oldest()
		print(question)
		if question:
			update.message.reply_text(str(question))
			question.remove()

			global count
			count -= 1

		else:
			update.message.reply_text("Não existem perguntas a serem respondidas")
	else:
		update.message.reply_text("Perdão, mas você não tem permissão de consultar as perguntas")

#function to end question mode
def done(bot,update):
	update.message.reply_text("Obrigado!")
	return ConversationHandler.END

#################
## Main script ##
#################

#get Updater object
updater = Updater(bot_token)

#get the dispatcher from Updater, which cotnains the event handlers
dp = updater.dispatcher

#conversation that represents the question mode
conversation = ConversationHandler(
	entry_points=[CommandHandler("question",question_entry_point)],
	states={
		"WAITING_QUESTION": [MessageHandler(Filters.all,store_question)]
	},
	fallbacks=[
		CommandHandler('done', done)
	]
)

#addign the conversation to the dispatcher
dp.add_handler(conversation)

#adding some commands
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("questions",get_oldest_question))
dp.add_handler(MessageHandler(Filters.all, start))

#starting bot
updater.start_polling()
updater.idle()
