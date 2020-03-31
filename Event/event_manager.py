import socket
import pickle
import uuid

from exchange_server_manager import ExchangeServer
from Event.order_event import OrderEvent
from Event.exchange_order_event import ExchangeOrderEvent

class EventManager:
	def __init__(self, port):
		self._host = socket.gethostname()
		self._port = port
		self._sock = self._setup_socket_for_communication()

	def _setup_socket_for_communication(self):
		sock = socket.socket()
		sock.connect((self._host, self._port))
		return sock
	
	def close_connection(self):
		self._sock.close()

	def send_event_to_exchange(self, event):
		data_string_to_send = pickle.dumps(event)
		self._sock.send(data_string_to_send)
		reply_from_exchange = self._sock.recv(4096)
		reply_exchange_event = pickle.loads(reply_from_exchange)
		
		return reply_exchange_event


if __name__ == '__main__':
	player_id = 'asdasdasd'
	symbol = 'YESBANK_EQ'
	price = 1000
	direction = 'LONG'
	quantity = 50

	event = OrderEvent(player_id, 'New', symbol, price, direction, quantity)
	em = EventManager(socket.gethostname, 12345)
	em.send_event_to_exchange(event)