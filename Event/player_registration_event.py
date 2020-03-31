from Event.event import Event 

class PlayerRegistrationEvent(Event):
	def __init__(self, player_name, player_id=None):
		Event.__init__(self, player_id)
		self._event_type = 'REGISTER'
		self._player_name = player_name