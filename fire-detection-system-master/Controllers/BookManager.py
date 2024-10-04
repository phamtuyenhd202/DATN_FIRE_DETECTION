from App.Books import Books

class BookManager():
	def __init__(self, DAO):
		self.misc = Books(DAO.db.book)
		self.dao = self.misc.dao


	def list(self):
		return self.dao.list()

	def getAllEmail(self):
		return self.dao.getAllEmail()


	def add(self, name, noti_email):
		return self.dao.add(name, noti_email)


	def get(self, id):
		return self.dao.get(id)


	def update(self, id, name, noti_email):
		return self.dao.update(id, name, noti_email)


	def delete(self, id):
		return self.dao.delete(id)

	def getReserverdBooksByUser(self, user_id):
		books = self.dao.getReserverdBooksByUser(user_id)

		return books

	def getBook(self, id):
		books = self.dao.getBook(id)

		return books

	def search(self, keyword, availability=1):
		books = self.dao.search_book(keyword, availability)

		return books

	def reserve(self, user_id, book_id):
		books = self.dao.reserve(user_id, book_id)

		return books

	def getUserBooks(self, user_id):
		books = self.dao.getBooksByUser(user_id)

		return books

	def getUserBooksCount(self, user_id):
		books = self.dao.getBooksCountByUser(user_id)

		return books










