from player import Player
from event_manager import EventManager
from db_connector import DbConnector
from data_listener import BookListener

initial_money = 10000
player_name = 'Notroop'

em = EventManager()
conn = DbConnector('postgres', 5432, 'postgres', '127.0.0.1')
file_path = 'D:\\genericbacktesters\\book_data\\file.dat'
bl = BookListener('', 12347, file_path)

player = Player(initial_money, player_name, em, conn)

symbol = 'YESBANK_EQ'
price = 1000
direction = 'SHORT'
quantity = 50
order_id = '9f04581c-a00b-4cd1-bb07-fd25ecf64315'
player.place_new_order(symbol, price, direction, quantity)
