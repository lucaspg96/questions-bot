from bson import ObjectId
from pymongo import MongoClient

#generic MongoDB document model
class AbstractMongo(dict): 

	__getattr__ = dict.get
	__delattr__ = dict.__delitem__
	__setattr__ = dict.__setitem__

	#save in the database
	def save(self):
		#new document, must insert on database
		if not self._id:
			self.collection.insert(self)
		#an existing document, must update
		else:
			self.collection.update(
				{ "_id": ObjectId(self._id) }, self)

	#load from the database
	def reload(self):
		if self._id:
			self.update(self.collection\
					.find_one({"_id": ObjectId(self._id)}))

	#remove from the database
	def remove(self):
		if self._id:
			self.collection.remove({"_id": ObjectId(self._id)})
			self.clear()

#question model
class Question(AbstractMongo):
	#defining the collection
	collection = MongoClient()["telegram"]["questions"]

	@staticmethod
	def get_oldest():
		"""
		Method to retreive, if we have, a question from the database.

		Return
		------

		question: Question object or None
				an instance of Question class containing the oldest question inserted at the database
		"""
		try:
			doc = Question.collection.find().sort([("time",1)]).limit(1)[0]
		
			return Question(doc)

		except Exception:
			return None

	@staticmethod
	def count():
		"""
		Method to get the number of question at the database

		Return
		------

		count: Integer
				number of questions at the database
		"""
		return Question.collection.count()

	def __str__(self):
		"""
		Object's String representation

		Return
		------

		string: String
				Question stringfied
		"""
		return """
Usuário: {} ({})
Hora: {}

Pergunta: {}""".format(self.user_name,self.user_tag,self.time,self.text)

