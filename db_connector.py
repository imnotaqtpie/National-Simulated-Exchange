import psycopg2


class DbConnector:
	def __init__(self, user, port, database, host, password='admin'):
		try:
			self._connection = psycopg2.connect(user = user,
											password = password,
											port = port,
											database = database,
											host = host)

			self._cursor = self._connection.cursor()
		except Exception as e:
			print(f"Error : {e}")

	def execute(self, query, *args):
		try:
			self._cursor.execute(query, args)
		except Exception as e:
			print(f'Error : {e}')
			self._connection.rollback()
			return None
		self._connection.commit()

	def executeNoCommit(self, query, *args):
		try:
			self._cursor.execute(query, args)
		except:
			self._connection.rollback()
			return None
		return True

	def select(self, query, *args):
		try:
			self._cursor.execute(query, args)
			cols = [desc[0] for desc in self._cursor.description]
		except Exception as e:
			print(f'Error : {e}')
			return None, None
		return self._cursor.fetchall(), cols

	def commit(self):
		self._connection.commit()