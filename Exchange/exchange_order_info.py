class OrderInfo:
	def __init__(self, symbol_id, price, direction, quantity, last_updated_time, pid):
		self._symbol_id = symbol_id
		self._price = price
		self._direction = direction
		self._quantity = quantity
		self._last_updated_time = last_updated_time 
		self._pid = pid 