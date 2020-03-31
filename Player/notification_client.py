import socket
import pickle

class NotificationClient:
	def __init__(self, host, port):
		self._host = host
		self._port = port
		self._sock = self._setup_socket_for_communication()

	def _setup_socket_for_communication(self):
		sock = socket.socket()
		sock.connect((self._host, self._port))
		return sock

	def listen_forever(self ):
		size = 4096
		while True:
			try:
				event_data = pickle.laods(self._sock.recv(size))
			except:
				continue

			if event_data:
				NotificationConfirmEvent(self._host, 'CON')
				yield event_datas