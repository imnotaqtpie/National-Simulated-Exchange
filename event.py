import time 
from enum import Enum

class Direction(Enum):
	LONG = 1
	SHORT = -1

class Event:
	def __init__(self, sender_id):
		self._sender_id = sender_id
		self._time_stamp = time.time()

class OrderEvent(Event):
	def __init__(self, player_id, order_type, symbol=None, price=None, direction=None, quantity=None, order_id=None):
		Event.__init__(self, player_id)
		self._event_type = 'ORDER'
		self._order_type = order_type
		self._symbol = symbol
		self._order_id = order_id
		self._price = price
		self._direction = direction
		self._quantity = quantity

		if not self._verify_order_validity():
			raise Exception('InvalidOrderError')

	def _verify_order_validity(self):
		return True
		if self._order_type == 'New':
			if not self._symbol or not self._price or not self._direction or not self._quantity:
				return False
			if not type(self._symbol) == str or not type(self._price) == float or not type(self._quantity) == int or not isinstance(self._direction, Direction):
				return False
		elif self._order_type == 'Modify':
			if not self._order_id or not self._price or not self._direction or not self._quantity:
				return False
			if not type(self._order_id) == str or not type(self._price) == float or not type(self._quantity) == int or not isinstance(self._direction, Direction):
				return False
		elif self._order_type == 'Delete':
			if not self._order_id:
				return False
			if not type(self._order_id) == str:
				return False
		else:
			return False
		return True

class ExchangeOrderEvent(Event):
	def __init__(self, sender_id, status, order_id=None, message=None):
		Event.__init__(self, sender_id)
		self._order_id = order_id
		self._status = status
		self._message = message

class PlayerRegistrationEvent(Event):
	def __init__(self, player_name, player_id=None):
		Event.__init__(self, player_id)
		self._event_type = 'REGISTER'
		self._player_name = player_name

class ExchangeRegistrationEvent(Event):
	def __init__(self, exchange_id, status, player_id=None, message=None):
		Event.__init__(self, exchange_id)
		self._event_type = 'REGISTER'
		self._status = status
		self._player_id = player_id
		self._message = message