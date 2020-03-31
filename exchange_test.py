from Common.db_connector import DbConnector
 
from Event.order_event import OrderEvent

from Exchange.exchange import Exchange
from Exchange.casting_server import CastingServer
from Exchange.matching_engine import MatchingEngine 
from Exchange.notification_server import NotificationServer

conn = DbConnector('postgres', 5432, 'exchangedb', '127.0.0.1')
cs = CastingServer('', 12346)
ns = NotificationServer('', 12121)
ex = Exchange(conn, ns, cs)
	
player_id = 'asdasdasd'
symbol = 'YESBANK_EQ'
price = 10.0
direction = 'LONG'
quantity = 30

event1 = OrderEvent(player_id, 'New', symbol, price, direction, quantity)
event2 = OrderEvent(player_id, 'Modify', 'YESBANK_EQ', price, 'SHORT', quantity, '292b93bb-ac8a-4e0c-b00c-7399c993c427')
#reply = ex.handle_order(event1)

ex.handle_order(event2)
print(reply._status, reply._order_id, reply._message)