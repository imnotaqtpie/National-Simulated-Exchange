import socket
import threading
import pickle 
import time

class CastingServer:
	def __init__(self, host, port):
		self._host = host
		self._port = port
		self._sock = self._initialise_socket(self._host, self._port)

	def _initialise_socket(self, host, port):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.settimeout(0.2)
		sock.bind((self._host, self._port))
		return sock

	def cast_to_all_clients(self, data):
		try:
			self._sock.sendto(pickle.dumps(data), ('<broadcast>', 12348))
			print(f'sent to {self._port}')
		except:
			return False
		return True


if __name__ == '__main__':
	print('starting')
	cs = CastingServer('', 12346)
	i = 0
	while True:
		data = b'random stuff %s', i
		cs.cast_to_all_clients(data)
		print(data)
		i += 1