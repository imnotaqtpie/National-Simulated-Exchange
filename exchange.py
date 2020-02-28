import uuid
from db_connector import DbConnector 
from enum import Enum 
from exchange_db_query import ExchangeDbQuery
from event import ExchangeOrderEvent, Direction, ExchangeRegistrationEvent


class Status:
	Error = -1
	Confirm = 0
	Reject = 1

class Reply:
	SenderFailureReject = "Rejected. Unrecognised sender"
	SymbolFailureReject = "Rejected. Unrecognised symbol"

class Exchange:
	BOOK_EXTENSION = 'ORDER_BOOK'
	
	def __init__(self, conn, casting_server, matching_engine=None):
		self._conn = conn
		self._casting_server = casting_server
		self._matching_engine = matching_engine
		
		self._exchange_id = '-1'
		self._symbols = self._get_all_symbols()
		self._registered_players = self._get_all_players()
		self._clients = []
		self._order_books = self.initialise_and_clear_order_book_for_all_symbols()

	def initialise_and_clear_order_book_for_all_symbols(self):
		books = {}
		sides = ['LONG', 'SHORT']
		for symbol in self._symbols:
			book_name = '_'.join((self.BOOK_EXTENSION, str(symbol)))
			books[book_name] = {}
			for side in sides:
				books[book_name][side] = {}

		return books

	def handle_player_registration(self, event):
		print('handling registration')
		query = ExchangeDbQuery.get_all_player_names_query()
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			return None
		player_names = [rows[i][cols.index('player_name')] for i in range(len(rows))]
		if event._player_name not in player_names:
			player_id = str(uuid.uuid4())
			query = ExchangeDbQuery.insert_new_user_to_db_query().format(player_id, event._player_name)
			self._conn.execute(query)
		else:
			query = ExchangeDbQuery.get_player_id_for_name_query().format(event._player_name)
			rows, cols = self._conn.select(query)
			if not rows or not cols:
				return None
			else:
				player_id = rows[0][cols.index('player_id')]

		return ExchangeRegistrationEvent(self._exchange_id, Status.Confirm, player_id)		

	def get_symbol_id_from_db(self, symbol):
		query = ExchangeDbQuery.get_symbol_id_for_name_query().format(symbol)
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			return None
		symbol_id = rows[0][cols.index('symbol_id')]
		return symbol_id

	def _get_all_players(self):
		query = ExchangeDbQuery.fetch_player_id_query()
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			raise Exception("DbError")

		players = [rows[i][cols.index('player_id')] for i in range(len(rows))]
		return players

	def _get_all_symbols(self):
		query = ExchangeDbQuery.fetch_symbols_from_db_query()
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			raise Exception("DbError")

		symbols = [rows[i][cols.index('symbol_id')] for i in range(len(rows))]
		return symbols

	def _verify_symbol(self, symbol_id):
		symbol = self.get_symbol_id_from_db(symbol_id)
		if symbol not in self._symbols:
			return False
		return True

	def _verify_order_sender(self, sender_id):
		if sender_id not in self._registered_players:
			return False
		return True

	def _verify_order(self, order_id):
		query = ExchangeDbQuery.fetch_order_from_db_query().format(order_id)
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			raise Exception("DbError")

		orders = [rows[i][cols.index('order_id')] for i in range(len(rows))]
		if order_id not in orders:
			return False
		return True

	def _generate_order_id(self):
		return str(uuid.uuid4())

	def get_order_info(self, order_id):
		query = ExchangeDbQuery.get_all_info_of_order().query(order_id)
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			return None, None, None, None

		symbol_id = rows[0][cols.index('symbol_id')]
		price = rows[0][cols.index('price')]
		quantitiy = rows[0][cols.index('quantitiy')]
		if quantitiy < 0:
			direction = 'SHORT'
		else:
			direction = 'LONG'

		return symbol_id, price, direction, quantitiy

	def _add_order_to_order_book(self, event):
		symbol_id = self.get_symbol_id_from_db(event._symbol)
		book_name = '_'.join((self.BOOK_EXTENSION, str(symbol_id)))

		try:
			self._order_books[book_name][event._direction][str(event._price)] += event._quantity
		except:
			self._order_books[book_name][event._direction][str(event._price)] = event._quantity

		order_id = self._generate_order_id()
		return order_id
		
	def _modify_order_in_order_book(self, event):
		symbol_id, price, direction, quantitiy = self.get_order_info(event._order_id)
		if not symbol_id:
			return ExchangeOrderEvent(self._exchange_id, Status.Reject)
		book_name = '_'.join((self.BOOK_EXTENSION, symbol_id))

		self._order_books[book_name][direction][str(price)] -= event._quantity
		
		try:
			self._order_books[book_name][event._direction][str(event._price)] += event._quantity
		except:
			self._order_books[book_name][event._direction][str(event._price)] = event._quantity
		
		self._exchange.check_symbol_for_trade(symbol_id)
		return ExchangeOrderEvent(self._exchange_id, Status.Confirm)

	def _delete_order_from_order_book(self, event):
		symbol_id, price, direction, quantitiy = self.get_order_info(event._order_id)
		if not symbol_id:
			return ExchangeOrderEvent(self._exchange_id, Status.Reject)
		book_name = '_'.join((self.BOOK_EXTENSION, symbol_id))

		self._order_books[book_name][direction][str(price)] -= event._quantity
		self._exchange.check_symbol_for_trade(symbol_id)
		return ExchangeOrderEvent(self._exchange_id, Status.Confirm)		

	def handle_new_orders(self, event):
		status = Status.Error
		reply_event = ExchangeOrderEvent(self._exchange_id, status)
		if not self._verify_symbol(event._symbol):
			reply_event._status = Status.Reject
			reply_event._message = Reply.SymbolFailureReject
			return reply_event

		order_id = self._add_order_to_order_book(event)
		if order_id:
			symbol_id = self.get_symbol_id_from_db(event._symbol)
			query = ExchangeDbQuery.add_order_to_orders_table_query().format(event._sender_id, order_id, symbol_id, event._price, event._quantity * Direction[event._direction].value)
			self._conn.execute(query)
			return ExchangeOrderEvent(self._exchange_id, Status.Confirm, order_id)
			self._exchange.check_symbol_for_trade(symbol_id)
		else:
			return ExchangeOrderEvent(self._exchange_id, Status.Reject)

	def handle_mod_orders(self, event):
		status = Status.Error
		reply_event = ExchangeOrderEvent(self._exchange_id, status)
		if not self._verify_order():
			reply_event._status = Status.Reject
			reply_event._message = Reply.OrderFailureReject
			return reply_event

		query = ExchangeDbQuery.update_order_in_orders_table_query().format(event._price, event._quantity * Direction[self._event.direction].value, event._order_id)
		self._conn.execute(query)
		
		return self._modify_order_in_order_book(event)

	def handle_del_event(self, event):
		status = Status.Error
		reply_event = ExchangeOrderEvent(self._exchange_id, status)
		if not self._verify_order_sender(event._sender_id):
			reply_event._status = Status.Reject
			reply_event._message = Reply.SenderFailureReject
			return reply_event

		query = ExchangeOrderEvent.delete_order_in_orders_table_query().format(event._symbol_id)
		self._conn.execute(query)

		return self._delete_order_from_order_book(event)

	def handle_order(self, ev):
		print('entered event handler')
		status = Status.Error
		reply_event = ExchangeOrderEvent(self._exchange_id, status)
		if not self._verify_order_sender(ev._sender_id):
			reply_event._status = Status.Reject
			reply_event._message = Reply.SenderFailureReject
			return reply_event

		if ev._order_type == 'New':
			reply_event = self.handle_new_orders(ev)
		if ev._order_type == 'Modify':
			reply_event = self.handle_mod_orders(ev)
		if ev._order_type == 'Delete':
			reply_event = self.handle_del_orders(ev)

		if reply_event._status == Status.Confirm:
			self._casting_server.cast_to_all_clients(self._order_books)

		print(self._order_books)
		return reply_event

	def handle_trade_event(self, event):
		pass


"""
	def _initialise_order_book(self, book_name):
		query = ExchangeDbQuery.create_new_table_for_order_book_query().format(book_name)
		try:
			self._conn.execute(query)
		except:
			raise Exception("Error creating table")

	def _clear_order_book(self, book_name):
		query = ExchangeDbQuery.clear_order_book_query().format(book_name)
		try:
			self._conn.execute(query)
		except:
			raise Exception("Error clearing table")

	def initialise_and_clear_order_book_for_all_symbols(self):
		for symbol in self._symbols:
			book_name = '_'.join((BOOK_EXTENSION, str(symbol)))
			query = ExchangeDbQuery.check_for_table_in_db_query().format(book_name)
			rows, cols = self._conn.select(query)
			if not rows:
				self._initialise_order_book(book_name)
			else:
				self._clear_order_book(book_name)
"""