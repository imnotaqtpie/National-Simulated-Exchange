from exchange import Exchange
from db_connector import DbConnector 
from event import OrderEvent
from casting_server import CastingServer

conn = DbConnector('postgres', 5432, 'exchangedb', '127.0.0.1')
cs = CastingServer('', 12346)
ex = Exchange(conn, cs)
player_id = 'asdasdasd'
symbol = 'YESBANK_EQ'
price = 1000
direction = 'SHORT'
quantity = 50

event = OrderEvent(player_id, 'New', symbol, price, direction, quantity)

reply = ex.handle_order(event)

print(reply._status, reply._order_id, reply._message)