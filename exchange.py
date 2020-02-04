class Exchange:
	def __init__(self, instruments):
		self._instruments = instruments
		self._book = self.init_books_for_instruments()

	def init_books_for_instruments(self):
		books = {}
		for instrument in instruments:
			books[instrument] = Book(instrument)
		return books