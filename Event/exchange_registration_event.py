from Event.event import Event 

class ExchangeRegistrationEvent(Event):
	def __init__(self, exchange_id, status, player_id=None, message=None):
		Event.__init__(self, exchange_id)
		self._event_type = 'REGISTER'
		self._status = status
		self._player_id = player_id
		self._message = message