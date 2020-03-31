from Event.event import Event 

class ConfirmEvent(Event):
	def __init__(self, sender_id = None):
		Event.__init__(self, sender_id)
		self._event_type = 'CONFIRM'
		self.status = 'CON'