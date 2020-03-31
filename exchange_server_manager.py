import socket
import threading
import pickle 

from Common.db_connector import DbConnector

from Exchange.exchange import Exchange
from Exchange.casting_server import CastingServer
from Exchange.matching_engine import MatchingEngine
from Exchange.notification_server import NotificationServer
 
class ExchangeServer:	
	def __init__(self, host, port, exchange):
		self._host = host
		self._port = port
		self._exchange = exchange
		self._sock = self._initialise_socket()
		self._connected_players = {}
		threading.Thread(target=self.listen_for_clients, args = ()).start()

	def _initialise_socket(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((self._host, self._port))
		return sock

	def listen_for_clients(self):
		print(f'Listening on port {self._port}')
		self._sock.listen(5)
		while True:
			client, address = self._sock.accept()
			client.settimeout(10000)

			print(f'connected players : {self._connected_players}')
			threading.Thread(target = self.listen_to_client, args = (client, address)).start()

	def listen_to_client(self, client, address):
		size = 4096
		while True:
			try:
				try:
					event_data = pickle.loads(client.recv(size))
				except:
					continue
				response = False
				if event_data._event_type == 'ORDER':
					response = self._exchange.handle_order(event_data)
				elif event_data._event_type == 'REGISTER':
					response = self._exchange.handle_player_registration(event_data)
					self._connected_players[event_data._player_name] = client
					self.update_exchange_client_list()

				client.send(pickle.dumps(response))

			except Exception as e:
				print(e)
				#self._connected_players.remove(client)
				#self.update_exchange_client_list()
				print(f'closing for client {client} due to inactivity')
				client.close()
				return False

	def update_exchange_client_list(self):
		self._exchange._clients = self._connected_players
		self._exchange.update_player_id_to_name_mapper()

if __name__ == '__main__':
	conn = DbConnector('postgres', 5432, 'exchangedb', '127.0.0.1')
	cs = CastingServer('', 12346)
	ns = NotificationServer('', 12121)
	ex = Exchange(conn, ns, cs)
	server = ExchangeServer('', 12345, ex)