class BookDAO():
	def __init__(self, DAO):
		self.db = DAO
		self.db.table = "books"

	def list(self):
		query = "SELECT id, name, noti_email FROM @table"
		books = self.db.query(query)
		return books.fetchall()

	def add(self, name, noti_email):
		query = f"INSERT INTO @table (name, noti_email) VALUES ('{name}', '{noti_email}')"
		self.db.query(query)
		self.db.commit()

	def get(self, id):
		query = f"SELECT id, name, noti_email FROM @table WHERE id = {id}"
		book = self.db.query(query)
		return book.fetchone()

	def update(self, id, name, noti_email):
		query = f"UPDATE @table SET name = '{name}', noti_email = '{noti_email}' WHERE id = {id}"
		self.db.query(query)
		self.db.commit()

	def delete(self, id):
		query = f"DELETE FROM @table WHERE id = {id}"
		self.db.query(query)
		self.db.commit()

	def reserve(self, user_id, book_id):
		if not self.available(book_id):
			return "err_out"

		q = self.db.query("INSERT INTO reserve (user_id, book_id) VALUES('{}', '{}');".format(user_id, book_id))

		self.db.query("UPDATE @table set count=count-1 where id={};".format(book_id))
		self.db.commit()

		return q

	def getBooksByUser(self, user_id):
		q = self.db.query(
			"select * from @table left join reserve on reserve.book_id = @table.id where reserve.user_id={}".format(
				user_id))

		books = q.fetchall()

		print(books)
		return books

	def getBooksCountByUser(self, user_id):
		q = self.db.query(
			"select count(reserve.book_id) as books_count from @table left join reserve on reserve.book_id = @table.id where reserve.user_id={}".format(
				user_id))

		books = q.fetchall()

		print(books)
		return books

	def getBook(self, id):
		q = self.db.query("select * from @table where id={}".format(id))

		book = q.fetchone()

		print(book)
		return book

	def available(self, id):
		book = self.getById(id)
		count = book['count']

		if count < 1:
			return False

		return True

	def getById(self, id):
		q = self.db.query("select * from @table where id='{}'".format(id))

		book = q.fetchone()

		return book


	def getAllEmail(self):
		query = ("SELECT noti_email FROM @table")

		books = self.db.query(query)

		return books.fetchall()




