from Event.event import Event 

class TradeReplyEvent(Event):
	def __init__(self, sender_id, order_id, quantity):
		Event.__init__(self, sender_id)
		self._order_id = order_id
		self._quantity = quantity