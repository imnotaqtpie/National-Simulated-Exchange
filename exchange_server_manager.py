import socket
import threading
import pickle 

from exchange import Exchange
from db_connector import DbConnector
from casting_server import CastingServer

class ExchangeServer:
	def __init__(self, host, port, exchange):
		self._host = host
		self._port = port
		self._exchange = exchange
		self._sock = self._initialise_socket(self._host, self._port)
		self._connected_players = []

	def _initialise_socket(self, host, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((self._host, self._port))
		return sock

	def listen_for_clients(self):
		self._sock.listen(5)
		while True:
			client, address = self._sock.accept()
			client.settimeout(10)
			self._connected_players.append(client)
			self.update_exchange_client_list()
			print(self._connected_players)
			threading.Thread(target = self.listen_to_client, args = (client, address)).start()

	def listen_to_client(self, client, address):
		size = 4096
		while True:
			try:
				event_data = pickle.loads(client.recv(size))
				response = False
				if event_data._event_type == 'ORDER':
					response = self._exchange.handle_order(event_data)
				elif event_data._event_type == 'REGISTER':
					response = self._exchange.handle_player_registration(event_data)
				else:
					raise Exception("Client disconnected")
				print(response)
				client.send(pickle.dumps(response))
			except Exception as e:
				print(e)
				self._connected_players.remove(client)
				self.update_exchange_client_list()
				print(f'closing for client {client} due to inactivity')
				client.close()
				return False

	def update_exchange_client_list(self):
		self._exchange._clients = self._connected_players


if __name__ == '__main__':
	conn = DbConnector('postgres', 5432, 'exchangedb', '127.0.0.1')
	cs = CastingServer('', 12346)
	
	ex = Exchange(conn, cs)
	server = ExchangeServer('', 12345, ex).listen_for_clients()