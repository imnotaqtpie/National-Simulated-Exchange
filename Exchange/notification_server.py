import socket
import threading
import pickle

from Event.confirm_event import ConfirmEvent

class NotificationServer:
	def __init__(self, host, port):
		self._host = socket.gethostname()
		self._port = port 
		self._sock = self._initialise_socket()
		self._connected_players = {}
		threading.Thread(target=self.listen_for_clients, args = ()).start()

	def _initialise_socket(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.bind((self._host, self._port))
		return sock 

	def listen_for_clients(self):
		print(f'notification server listening on port {self._port}')
		self._sock.listen(5)
		while True:
			client, address = self._sock.accept()
			client.settimeout(1000)
			threading.Thread(target = self.talk_to_client, args = (client, address)).start()
		
	def talk_to_client(self, client, address):
		size = 4096
		while True:
			try:
				event_data = pickle.loads(client.recv(size))
			except:
				continue

			if event_data._event_type == 'REGISTER':
				self._connected_players[event_data._player_name] = client
				print(self._connected_players)
				break
			
	def send_message_client(self, client, data):
		print('client : ' + str(client))
		size = 4096
		client.send(pickle.dumps(data))
		print('sent data')
		while True:
			response = pickle.loads(client.recv(size))
			print(response)
			if response._event_type == 'CONFIRM':
				return True