from Event.event import Event 

class TradeEvent(Event):
	def __init__(self, symbol, sender_id, buy_order_id, sell_order_id, buy_quantity, seller_quantity, buy_pid, sell_pid, buy_lut, sell_lut, price):
		Event.__init__(self, sender_id)
		self._event_type = 'TRADE'
		self._symbol = symbol
		self._LONG_order_id = buy_order_id
		self._SHORT_order_id = sell_order_id	
		self._LONG_quantity = buy_quantity
		self._SHORT_quantity = seller_quantity
		self._LONG_pid = buy_pid
		self._SHORT_pid = sell_pid
		self._LONG_lut = buy_lut
		self._SHORT_lut = sell_lut
		self._price = price