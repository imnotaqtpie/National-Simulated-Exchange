from Event.event import Event 

class ExchangeOrderEvent(Event):
	def __init__(self, sender_id, status, order_id=None, message=None):
		Event.__init__(self, sender_id)
		self._order_id = order_id
		self._status = status
		self._message = message
