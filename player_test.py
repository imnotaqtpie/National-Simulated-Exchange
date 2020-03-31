import socket

from Common.db_connector import DbConnector

from Event.event_manager import EventManager

from Player.player import Player
from Player.data_listener import BookListener

initial_money = 10000
player_name = 'Notroop'

em = EventManager(12345)
conn = DbConnector('postgres', 5432, 'postgres', '127.0.0.1')
file_path = 'D:\\genericbacktesters\\book_data\\file.dat'
bl = BookListener('', 12347, file_path)

player = Player(initial_money, player_name, socket.gethostname(), 12121, em, conn)

symbol = 'YESBANK_EQ'
price = 14
direction = 'LONG'
quantity = 37
order_id = '292b93bb-ac8a-4e0c-b00c-7399c993c427'
#player.place_new_order(symbol, float(price), direction, int(quantity))


player.place_new_order(symbol, float(price), direction, int(quantity))
inp = input()
direction = 'SHORT'
player.place_new_order(symbol, float(price), direction, int(quantity))


while True:
	inp = input('Enter order type: ')
	if inp.upper() == 'STOP':
		break

	if inp.upper() == 'NEW':
		price = input('Enter price : ')
		direction = input('Enter direction : ')
		quantity = input('Enter quantity : ')

		player.place_new_order(symbol, float(price), direction, int(quantity))

	if inp.upper() == 'MOD':
		order_id = input('Enter order_id : ')
		price = input('Enter new price : ')
		direction = input('Enter new direction : ')
		quantity = input('Enter new quantity : ')

		player.place_mod_order(order_id, price, direction, quantity)

	if inp.upper() == 'DEL':
		order_id = input('Enter order_id : ')
		player.place_del_order(order_id)