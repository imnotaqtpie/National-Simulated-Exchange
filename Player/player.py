import uuid
import threading 
import queue
import socket
import pickle

from enum import Enum

from Exchange.exchange import Status 
from Common.db_connector import DbConnector

from Event.event import Direction
from Event.order_event import OrderEvent 
from Event.player_registration_event import PlayerRegistrationEvent
from Event.event_manager import EventManager 
from Event.confirm_event import ConfirmEvent 

from Player.player_db_query import PlayerDbQuery
from Player.order_info import PlayerOrderInfo 

class Player:
	BUF_SIZE = 100

	def __init__(self, initial_money, player_name, notif_host, notif_port, event_manager, conn):
		self._event_manager = event_manager
		self._player_name = player_name
		self._notif_host = notif_host
		self._notif_port = notif_port
		self._conn = conn
		
		self._player_id = self.get_player_id_from_exchange()
		self._player_info = self._generate_player_info(player_name, initial_money)

		self._client = self._setup_notification_listener()
		print(f'client setup on host {self._notif_host} port {self._notif_port}')
		self._queue = list()
		self._lock = threading.Lock()
		
		self.setup_producer_and_consumer()		

		#self._available_symbols = Exchange._get_all_available_symbols() 

	def _setup_notification_listener(self):
		sock = socket.socket()
		sock.connect((self._notif_host, self._notif_port))
		return sock

	def setup_producer_and_consumer(self):
		print('creating producer and consumer')
		threading.Thread(target = self._setup_producer).start()
		threading.Thread(target = self._setup_consumer).start()

	def _setup_consumer(self):
		size = 4096
		re = PlayerRegistrationEvent(self._player_name)
		self._client.send(pickle.dumps(re))

		while True:
			try:
				event_data = pickle.loads(self._client.recv(size))
			except:
				continue

			if event_data:
				self._client.send(pickle.dumps(ConfirmEvent(self._notif_host)))
				self._lock.acquire()
				self._queue.append(event_data)
				self._lock.release()

	def _setup_producer(self):
		while True:
			if len(self._queue) > 0:
				self._lock.acquire()
				trade_event = self._queue.pop()
				print(self._queue)
				self.handle_trade(trade_event)
				self._lock.release()

	def _send_event(self, event):
		return self._event_manager.send_event_to_exchange(event)

	def get_player_id_from_exchange(self):
		re = PlayerRegistrationEvent(self._player_name)
		return self._send_event(re)._player_id

	def _get_all_available_symbols_from_db(self):
		query = PlayerDbQuery.fetch_all_symbols_query()
		rows, cols = self._conn.select(query)
		return [rows[i][cols.index('symbol_name')] for i in range(len(rows))]	

	def _generate_player_info(self, name, money):
		info = {}
		info['Player_name'] = name
		info['Credit'] = money
		info['Symbols'] = self._get_all_available_symbols_from_db()
		return info
		
	def _handle_new_con(self, event, order_id):
		if event._symbol in self._player_info['Symbols']:
			#update db with new values for symbol
			query = PlayerDbQuery.fetch_details_of_symbol_query().format(event._symbol)
			try:
				rows, cols = self._conn.select(query)
			except:
				return

			if not rows:
				raise Exception("DbError")
			quantity = rows[0][cols.index('quantity')]
			open_orders = rows[0][cols.index('open_orders')] + ( event._quantity * Direction[event._direction].value ) 
			query = PlayerDbQuery.update_symbols_db_query().format(quantity, open_orders, event._symbol)
			self._conn.execute(query)
		else:
			self._player_info['Symbols'] += [event._symbol]
			#insert new symbol into db
			quantity = 0
			open_orders = event._quantity * Direction[event._direction].value
			query = PlayerDbQuery.insert_new_symbol_db_query().format(event._symbol, quantity, open_orders)
			self._conn.execute(query)

		#insert order into db
		quantity = event._quantity * Direction[event._direction].value
		query = PlayerDbQuery.insert_order_details_into_order_table_query().format(order_id, event._symbol, quantity, event._price)
		self._conn.execute(query)
		print('Orders added to db and committed')

	def _handle_mod_con(self, event, old_quantity, order_id):
		#update symbols table for the symbol
		query = PlayerDbQuery.fetch_details_of_symbol_query().format(event._symbol)
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			raise Exception("DbError")
		quantity = rows[0][cols.index('quantity')]
		open_orders = rows[0][cols.index('open_orders')] + ( old_quantity - event._quantity * Direction[event._direction].value )
		query = PlayerDbQuery.update_symbols_db_query().format(quantity, open_orders, event._symbol)
		self._conn.execute(query)

		#update order table with new order_info
		quantity = event._quantity * Direction[event._direction].value
		query = PlayerDbQuery.update_order_details_into_order_table_query().format(quantity, event._price, order_id)
		self._conn.execute(query)
		print('Orders modified to db and committed')

	def _handle_del_con(self, symbol, quantity, price, order_id):
		#update credit
		self._player_info['Credit'] += quantity * price
		#update symbol table
		query = PlayerDbQuery.fetch_details_of_symbol_query().format(symbol)
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			raise Exception("DbError")
		quantity = rows[0][cols.index('quantity')]
		open_orders = rows[0][cols.index('open_orders')] - quantity
		query = PlayerDbQuery.update_symbols_db_query().format(quantity, open_orders, symbol)
		self._conn.execute(query)

		#remove order from order table
		query = PlayerDbQuery.remove_order_from_order_table_query().format(order_id)
		self._conn.execute(query)

	def _handle_new_rej(self, event):
		print('event rejected')
		self._player_info['Credit'] += (event._price * Direction[event._direction].value * event._quantity)

	def _handle_mod_rej(self, event, old_value):
		net_value = (old_value - event._price * Direction[event._direction].value * event._quantity)
		self._player_info['Credit'] += net_value

	def _handle_del_rej(self):
		pass

	def _fetch_order_info(self, order_id):
		query = PlayerDbQuery.fetch_details_of_order_query().format(order_id)
		rows, cols = self._conn.select(query)
		if not rows or not cols:
			return None
		return PlayerOrderInfo(rows[0][cols.index('symbol_name')], rows[0][cols.index('quantity')], rows[0][cols.index('price')])

	def place_new_order(self, symbol, price, direction, quantity):
		event = OrderEvent(self._player_id, 'New', symbol, price, direction, quantity)
		if self._player_info['Credit'] - ( price * Direction[direction].value * quantity ) < 0:
			return None
		self._player_info['Credit'] -= ( price * Direction[direction].value * quantity )
		
		return_signal = self._send_event(event)

		if return_signal._status == Status.Confirm:
			self._handle_new_con(event, return_signal._order_id)
		else:
			self._handle_new_rej(event)

		return return_signal

	def place_mod_order(self, order_id, price, direction, quantity):
		order_info = self._fetch_order_info(order_id) 	
		old_symbol, old_quantity, old_price = order_info._symbol_name, order_info._quantity, order_info._price
		if not old_symbol:
			return None
		event = OrderEvent(self._player_id, 'Modify', old_symbol, price, direction, quantity, order_id)
		if old_quantity * old_price - quantity * price * Direction[direction].value > self._player_info['Credit']:
			return None

		self._player_info['Credit'] -= ( old_quantity * old_price - quantity * price * Direction[direction].value)

		return_signal = self._send_event(event)
		print(return_signal._status)
		if return_signal._status == Status.Confirm:
			self._handle_mod_con(event, old_quantity * Direction[direction].value, order_id)
		else:
			self._handle_mod_rej(event, old_quantity * old_price)
 
		return return_signal

	def place_del_order(self, order_id):
		event = OrderEvent(self._player_id, 'Delete', order_id = order_id)
		order_info = self._fetch_order_info(order_id)
		old_symbol, old_quantity, old_price = order_info._symbol_name, order_info._quantity, order_info._price
		if not old_symbol:
			return None

		if old_quantity * old_price + self._player_info['Credit'] < 0:
			return None

		return_signal = self._send_event(event) 

		if return_signal._status == Status.Confirm:
			self._handle_del_con(old_symbol, old_quantity, old_price, order_id)
		else:
			self._handle_del_rej(order_id)

		return return_signal

	def handle_trade(self, event):
		#symbol = self._fetch_order_info(event._order_id)._symbol_name
		print('Handling trade')
		symbol = 'YESBANK_EQ'
		#update credit
		#update symbol table
		query = PlayerDbQuery.fetch_details_of_symbol_query().format(symbol)
		print(query)
		
		self._conn._cursor.execute(query)
		cols = [desc[0] for desc in self._conn._cursor.description]
		try:
			rows = self._conn._cursor.fetchone()
		except Exception as e:
			print(e)
			pass
		if not rows or not cols:
			raise Exception("DbError")
		quantity = rows[cols.index('quantity')] + event._quantity
		open_orders = rows[cols.index('open_orders')] - event._quantity
		query = PlayerDbQuery.update_symbols_db_query().format(quantity, open_orders, symbol)
		self._conn.execute(query)

		#remove order from order table
		query = PlayerDbQuery.remove_order_from_order_table_query().format(event._order_id)
		self._conn.execute(query)
		print(rows, cols)
		print('completed')