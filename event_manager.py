import socket
import pickle
import uuid

from exchange_server_manager import ExchangeServer
from event import OrderEvent, ExchangeOrderEvent

class EventManager:
	def __init__(self, ):
		self._host =  socket.gethostname()
		self._port = 12345

		self._sock = self._setup_socket_for_communication()

	def _setup_socket_for_communication(self):
		sock = socket.socket()
		sock.connect((self._host, self._port))
		return sock
	
	def close_connection(self):
		self._sock.close()

	def listen_to_server(self):
		size = 4096
		while True:
			try:
				data = pickle.loads(self._sock.recv(size))
				print(data)
			except:
				pass

	def send_event_to_exchange(self, event):
		data_string_to_send = pickle.dumps(event)
		self._sock.send(data_string_to_send)
		reply_from_exchange = self._sock.recv(4096)
		reply_exchange_event = pickle.loads(reply_from_exchange)
		
		print(reply_exchange_event._status)
		return reply_exchange_event

"""
	def send_event_to_exchange(self, event):
		status = Status.NEWCON
		order_id = uuid.uuid4()
		return_event = ExchangeOrderEvent('-1', status, order_id)
		return return_event
"""

if __name__ == '__main__':
	player_id = 'asdasdasd'
	symbol = 'YESBANK_EQ'
	price = 1000
	direction = 'LONG'
	quantity = 50

	event = OrderEvent(player_id, 'New', symbol, price, direction, quantity)
	em = EventManager()
	em.send_event_to_exchange(event)