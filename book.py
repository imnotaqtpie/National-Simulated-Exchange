class Orderbook:
	def __init__(self):
		self.order_history = []
		self._bid_book = {}
		self._bid_book_prices = {}
		self._ask_book = {}
		self._ask_book_prices = {}
		self.trade_book = []
		self._order_index = 0

	def _add_order_to_history(self, order):
		historical_order = {'order_id' = order['order_id'],
							'timestamp' = order['timestamp'],
							'order_type' = order['order_type'],
							'order_side' = order['order_side'],
							'order_volume' = order['order_volume'],
							'order_price' = order['order_price']}
		self._order_index += 1
		historical_order['exid'] = self._order_index
		self.order_history.append(historical_order)

	def handle_orders(self):
		pass

	def _add_order_to_book(self, order):
		book_order = {'order_id' = order['order_id'],
		   			  'timestamp' = order['timestamp'],
					  'order_type' = order['order_type'],
					  'order_side' = order['order_side'],
					  'order_volume' = order['order_volume'],
					  'order_price' = order['order_price']}

		if order['order_side'] == 'sell':
			book_prices = self._ask_book_prices
			book = self._ask_book
		elif order['order_side'] == 'buy':
			book_prices = self._bid_book_prices
			book = self._bid_book

		if order['order_price'] in book_prices:
			book['number_orders'] += 1
			book[order['order_price']]['size'] += order['order_volume']
			book[order['order_price']]['order_ids'].append(order['order_id'])
			book[order['order_price']][order['order_id']] = book_order
		else:
			bisect.insort(book_prices, order['price'])
			book[order['order_price']] = {'number_orders' : 1, 
										  'size' : order['order_volume'],
										  'order_id' : [order['order_id']],
										  'orders' : {order['order_id'] : book_order}}


	def _remove_order(self):
		pass

	def _modify_order(self):
		pass