import time 
from enum import Enum

class Direction(Enum):
	LONG = 1
	SHORT = -1

class Event:
	def __init__(self, sender_id):
		self._sender_id = sender_id
		self._time_stamp = time.time()