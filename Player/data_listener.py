import socket
import pickle
import os
import signal 

class BookListener:
	def __init__(self, host, port, file_path):
		self._host = host
		self._port = port
		self._sock = self._setup_socket_for_listen()
		try:
			self._file = open(file_path, 'w+')
		except:
			raise Exception('Invalid file path')

	def _setup_socket_for_listen(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		sock.bind((self._host, self._port))
		return sock

	def listen_forever(self):
		print('entering')
		while True:
			data, addr = self._sock.recvfrom(4096)
			print(data)
			if data:
				print('writing data')
				self.data_handler(data)
		signal.signal(signal.SIGINT, KeyboardInterruptHandler)

	def data_handler(self, data):
		try:
			self._file.writelines(str(pickle.loads(data)) + '\n')
			self._file.flush()
			print('wrote stuff')
		except Exception as e:
			print(e)
		return True

	def KeyboardInterruptHandler(self):
		self._sock.close()
		self._file.flush()
		self._file.close()
		exit(0)

if __name__ == '__main__':
	file_path = 'D:\\genericbacktesters\\book_data\\file.dat'
	bl = BookListener('', 12348, file_path)
	bl.listen_forever()