import uuid
from enum import Enum
from collections import OrderedDict
import numpy as np
import time

class Direction(Enum):
	LONG = 1
	SHORT = -1

class Status(Enum):
	PLACED = 0
	TRADED = 1
	REJECT = 2
	REMOVED = 3
	ERROR = -1

n_symbols = 5
n_players = 2
symbols = ['YESBANK_EQ','IBULHSGFIN_EQ','SBI_EQ','IDEA_EQ','RELINFRA_EQ']

player_ids = [str(uuid.uuid4()) for i in range(n_players)]

player_info = {}

for player in player_ids:
	player = str(player)
	player_info[player] = {}
	player_info[player]['player_name'] = 'Player' + str(player)
	player_info[player]['credit'] = 10000
	player_info[player]['holdings'] = {}
	player_info[player]['orders'] = {}
	for symbol in symbols:
		player_info[player]['holdings'][symbol] = 0
		player_info[player]['orders'][symbol] = 0

orders_info = OrderedDict()

order_book = {}
sides = ['LONG', 'SHORT']
for symbol in symbols:
	order_book[symbol] = {}
	for side in sides:
		order_book[symbol][side] = {}
		order_book[symbol][side][str(0.0)] = 0

def place_order(player_id, symbol, price, direction, quantity):
	order_id = str(uuid.uuid4())
	orders_info[order_id] = {}
	orders_info[order_id]['player_id'] = player_id
	orders_info[order_id]['symbol'] = symbol
	orders_info[order_id]['price'] = price
	orders_info[order_id]['direction'] = direction
	orders_info[order_id]['quantity'] = quantity
	orders_info[order_id]['status'] = Status.PLACED

	try:
		order_book[symbol][direction][str(price)] += quantity
	except:
		order_book[symbol][direction][str(price)] = quantity

	if direction == 'LONG':
		player_info[player_id]['orders'][symbol] += 1 * quantity
	else:
		player_info[player_id]['orders'][symbol] += -1 * quantity
	print('Order placed with the following details : ' , player_id, symbol, price, direction, quantity)
	
	return order_id

def modify_order(player_id, symbol, order_id, price, direction, quantity):
	print('Order modifying with the following details : ', order_id, player_id, symbol, price, direction, quantity)
	if orders_info[order_id]['status'] != Status.PLACED:
		return Status.REJECT

	old_price = str(orders_info[order_id]['price'])
	old_quantity = orders_info[order_id]['quantity']
	old_direction = orders_info[order_id]['direction']
	order_book[symbol][old_direction][old_price] -= old_quantity

	del orders_info[order_id]

	try:
		order_book[symbol][direction][str(price)] += quantity
	except:
		order_book[symbol][direction][str(price)] = quantity
		
	orders_info[order_id] = {}
	orders_info[order_id]['player_id'] = player_id
	orders_info[order_id]['symbol'] = symbol
	orders_info[order_id]['price'] = price
	orders_info[order_id]['direction'] = direction
	orders_info[order_id]['quantity'] = quantity
	orders_info[order_id]['status'] = Status.PLACED

	print('Order modified with the following details : ', order_id, player_id, symbol, price, direction, quantity)


def remove_order(player_id, order_id):
	if orders_info[order_id]['status'] != Status.PLACED:
		return Status.REJECT

	old_price = orders_info[order_id]['price']
	old_quantity = orders_info[order_id]['quantity']
	old_direction = orders_info[order_id]['direction']
	order_book[symbol][old_price][old_direction] -= old_quantity

	orders_info[order_id]['status'] = Status.REMOVED

def do_trade(symbol, price):
	buy_order_id = [i_d for i_d in list(orders_info.keys()) if orders_info[i_d]['price'] == price and orders_info[i_d]['direction'] == Direction.LONG and orders_info[i_d]['status'] == Status.PLACED][0]
	sell_order_id = [i_d for i_d in list(orders_info.keys()) if orders_info[i_d]['price'] == price and orders_info[i_d]['direction'] == Direction.SHORT and orders_info[i_d]['status'] == Status.PLACED][0]

	quantity = min(orders_info[buy_order_id]['quantity'], orders_info[sell_order_id]['quantity'])
 
	order_book[symbol][Direction.LONG][price] -= quantity
	order_book[symbol][Direction.SHORT][price] -= quantity

	orders_info[buy_order_id]['status'] = Status.TRADED
	orders_info[sell_order_id]['status'] = Status.TRADED

def check_trade(symbol):
	max_buy_price = max([float(a) for a in order_book[symbol][Direction.LONG]])
	min_sell_price = min([float(a) for a in order_book[symbol][Direction.SHORT]])

	if max_buy_price == min_sell_price:
		do_trade(symbol, price)

directions = ['LONG', 'SHORT']

def looper(n_iters=1000):
	ts = 0
	while ts < n_iters:
		if ts % 5 == 0:
			player_id = player_ids[np.random.randint(2)]
			symbol = symbols[np.random.randint(5)]
			price = np.random.randint(10)
			side = sides[np.random.randint(2)]
			quantity =  np.random.randint(30)
			order_id = place_order(player_id, symbol, price, side, quantity)
			modify_order(player_id, symbol, order_id, price + 3, side, quantity + 5)

	ts += 1
	time.sleep(10000)
looper() 