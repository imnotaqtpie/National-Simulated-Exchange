import uuid
import threading
import time

from enum import Enum 

from Common.db_connector import DbConnector 

from Event.exchange_order_event import ExchangeOrderEvent
from Event.event import Direction
from Event.exchange_registration_event import ExchangeRegistrationEvent
from Event.order_event import OrderEvent 
from Event.trade_reply_event import TradeReplyEvent

from Exchange.exchange_db_query import ExchangeDbQuery
from Exchange.matching_engine import MatchingEngine 
from Exchange.exchange_order_info import OrderInfo 
from Exchange.notification_server import NotificationServer

class Status:
	Error = -1
	Confirm = 0
	Reject = 1

class Reply:
	SenderFailureReject = "Rejected. Unrecognised sender"
	SymbolFailureReject = "Rejected. Unrecognised symbol"

class Exchange:
	BOOK_EXTENSION = 'ORDER_BOOK'
	
	def __init__(self, conn, notification_server, casting_server):
		self._conn = conn
		self._casting_server = casting_server
		self._matching_engine = MatchingEngine(self._conn)

		self._notification_server = notification_server
		self._symbol_name_to_id = self.initialise_symbol_name_to_id_mapper()
		self._player_id_to_name = self.update_player_id_to_name_mapper()
		self._exchange_id = '-1'
		self._symbols = self._get_all_symbols()
		self._registered_players = self._get_all_players()
		self._clients = []
		self._order_books = self.initialise_and_clear_order_book_for_all_symbols() 

	def initialise_symbol_name_to_id_mapper(self):
		query = ExchangeDbQuery.get_all_symbol_details_query()
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			raise Exception('DbError')
		symbol_names = [row[cols.index('symbol_name')] for row in rows]
		symbol_id = [row[cols.index('symbol_id')] for row in rows]
		return dict(zip(symbol_names, symbol_id))

	def update_player_id_to_name_mapper(self):
		query = ExchangeDbQuery.get_all_player_details_query()
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			raise Exception('DbError')
		player_ids = [row[cols.index('player_id')] for row in rows]
		player_names = [row[cols.index('player_name')] for row in rows]
		return dict(zip(player_ids, player_names))


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
			print('New registration')
			player_id = str(uuid.uuid4())
			query = ExchangeDbQuery.insert_new_user_to_db_query().format(player_id, event._player_name)
			self._conn.execute(query)
		else:
			print('getting old player id')
			query = ExchangeDbQuery.get_player_id_for_name_query().format(event._player_name)
			rows, cols = self._conn.select(query)
			if not rows or not cols:
				return None
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
		print(query)
		rows, cols = self._conn.select(query) 
		print(rows, cols)
		if not cols:
			raise Exception("DbError")
		if not rows:
			return False
		return True

	def _generate_order_id(self):
		return str(uuid.uuid4())

	def get_order_info(self, order_id):
		query = ExchangeDbQuery.get_all_info_of_order_query().format(order_id)
		print(query)
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			return None

		symbol_id = rows[0][cols.index('symbol_id')]
		price = rows[0][cols.index('price')]
		quantity = rows[0][cols.index('quantity')]
		last_updated_time = rows[0][cols.index('last_updated_time')]
		player_id = rows[0][cols.index('player_id')]
		if quantity < 0:
			direction = 'SHORT'
		else:
			direction = 'LONG'

		return OrderInfo(symbol_id, price, direction, quantity, last_updated_time, player_id)

	def _update_order_book_in_db(self, book_name, direction, price):
		try:
			quantity = self._order_books[book_name][direction][price]
		except:
			quantity = 0

		print(book_name, direction)
		book_name = '_'.join((book_name, direction))
		print(f"updating order book for table '{book_name}'")
		if quantity == 0:
			query = ExchangeDbQuery.delete_order_book_entry_from_db_query().format(book_name, price)
		else:
			query = ExchangeDbQuery.update_or_insert_order_book_entry_into_db_query().format(book_name, price, quantity, book_name, quantity, book_name, price)
	
		self._conn.execute(query)


	def _add_order_to_order_book(self, event):
		symbol_id = self.get_symbol_id_from_db(event._symbol)
		book_name = '_'.join((self.BOOK_EXTENSION, str(symbol_id)))

		try:
			self._order_books[book_name][event._direction][str(event._price)] += event._quantity
		except:
			self._order_books[book_name][event._direction][str(event._price)] = event._quantity

		self._update_order_book_in_db(book_name, event._direction, str(event._price))
		order_id = self._generate_order_id()
		return order_id
		
	def _modify_order_in_order_book(self, event): 
		order_info = self.get_order_info(event._order_id)
		symbol_id, price, direction, quantity, pid = order_info._symbol_id, order_info._price, order_info._direction, order_info._quantity, order_info._pid
		if not symbol_id:
			return ExchangeOrderEvent(self._exchange_id, Status.Reject)
		book_name = '_'.join((self.BOOK_EXTENSION, str(symbol_id)))

		try:
			self._order_books[book_name][direction][str(price)] -= event._quantity
		except:
			pass

		try:
			self._order_books[book_name][event._direction][str(event._price)] += event._quantity
		except:
			self._order_books[book_name][event._direction][str(event._price)] = event._quantity
		
		self._update_order_book_in_db(book_name, event._direction, str(event._price))
		return ExchangeOrderEvent(self._exchange_id, Status.Confirm)

	def _delete_order_from_order_book(self, event):
		order_info = self.get_order_info(event._order_id)
		symbol_id, price, direction, quantity, pid = order_info._symbol_id, order_info._price, order_info._direction, order_info._quantity, order_info._pid
		if not symbol_id:
			return ExchangeOrderEvent(self._exchange_id, Status.Reject)
		book_name = '_'.join((self.BOOK_EXTENSION, str(symbol_id)))
		print(self._order_books[book_name][direction][str(price)])
		self._order_books[book_name][direction][str(price)] -= quantity
			
		self._update_order_book_in_db(book_name, direction, str(price))

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
		if not self._verify_order(event._order_id):
			reply_event._status = Status.Reject
			reply_event._message = Reply.OrderFailureReject
			return reply_event

		reply_event = self._modify_order_in_order_book(event)

		query = ExchangeDbQuery.update_order_in_orders_table_query().format(event._price, event._quantity * Direction[event._direction].value, event._order_id)
		self._conn.execute(query)

		return reply_event

	def handle_del_orders(self, event):
		status = Status.Error
		reply_event = ExchangeOrderEvent(self._exchange_id, status)
		if not self._verify_order_sender(event._sender_id):
			reply_event._status = Status.Reject
			reply_event._message = Reply.SenderFailureReject
			return reply_event

		reply_event = self._delete_order_from_order_book(event)

		query = ExchangeDbQuery.delete_order_in_orders_table_query().format(event._order_id)
		self._conn.execute(query)

		return reply_event

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
			print(self._order_books)	
			self._casting_server.cast_to_all_clients(self._order_books)
			trade_ev = self._matching_engine.check_order_book(self._symbol_name_to_id[ev._symbol], self.BOOK_EXTENSION)
			print(f'trade_ev : {trade_ev}')
			if trade_ev != None:
				self.handle_trade_event(trade_ev)

		return reply_event

	def handle_trade_event(self, event):
		#modify partial trade
		qty_diff = event._LONG_quantity - abs(event._SHORT_quantity)
		quantity = min(event._LONG_quantity, abs(event._SHORT_quantity))

		partial_trader_dir = 'LONG' if qty_diff > 0 else 'SHORT'
		partial_trader_pid = event._LONG_pid if qty_diff > 0 else event._SHORT_pid
		partial_trader_oid = event._LONG_order_id if qty_diff > 0 else event._SHORT_order_id
		partial_trader_lut = event._LONG_lut if qty_diff > 0 else event._SHORT_lut

		full_trader_dir = 'SHORT' if qty_diff > 0 else 'LONG'
		full_trader_pid = event._SHORT_pid if qty_diff > 0 else event._LONG_pid
		full_trader_oid = event._SHORT_order_id if qty_diff > 0 else event._LONG_order_id
		full_trader_lut = event._SHORT_lut if qty_diff > 0 else event._LONG_lut

		book_name = '_'.join((self.BOOK_EXTENSION, str(event._symbol)))

		try:
			self._order_books[book_name][partial_trader_dir][str(int(event._price))] -= quantity
			del self._order_books[book_name][full_trader_dir][str(int(event._price))] 
		except Exception as e:
			print(e)

		
		self._update_order_book_in_db(book_name, full_trader_dir, str(int(event._price)))
		self._update_order_book_in_db(book_name, partial_trader_dir, str(int(event._price)))

		query = ExchangeDbQuery.update_order_in_orders_table_without_changing_time_query().format(event._price, qty_diff, partial_trader_lut, partial_trader_oid)
		self._conn.execute(query)
		
		query = ExchangeDbQuery.delete_order_in_orders_table_query().format(full_trader_oid)
		self._conn.execute(query)	

		print('traded on {} for {} quantity {}'.format(event._symbol, event._price, quantity))

		#ping to respective clients
		sign = 1 if full_trader_dir == 'LONG' else -1
		full_trader_reply_ev = TradeReplyEvent(self._exchange_id, full_trader_oid, sign * quantity)
		partial_trader_reply_ev = TradeReplyEvent(self._exchange_id, partial_trader_oid, -1 * sign * quantity)
		
		time.sleep(0.001)

		self._notification_server.send_message_client(self._notification_server._connected_players[self._player_id_to_name[full_trader_pid]], full_trader_reply_ev)
		self._notification_server.send_message_client(self._notification_server._connected_players[self._player_id_to_name[partial_trader_pid]], partial_trader_reply_ev)


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