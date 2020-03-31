from Event.trade_event import TradeEvent

from Exchange.exchange_db_query import ExchangeDbQuery

class MatchingEngine:
	def __init__(self, conn):
		self._conn = conn
		self._engine_id = 3000

	def check_order_book(self, symbol, book_ext):
		book_name = '_'.join((book_ext, str(symbol)))
		query = ExchangeDbQuery.get_top_level_order_book_data_query().format(book_name)
		rows, cols = self._conn.select(query)
		print(query)
		if not cols:
			raise Exception("DbError")
		if not rows: 
			return None

		price = rows[0][cols.index('price')]

		query = ExchangeDbQuery.get_earliest_buy_order_at_price_query().format(price, symbol)
		rows, cols = self._conn.select(query)
 
		buy_order_id = rows[0][cols.index('order_id')]
		buy_player_id = rows[0][cols.index('player_id')]
		buy_quantity = rows[0][cols.index('quantity')]
		buy_lut = rows[0][cols.index('last_updated_time')]

		query = ExchangeDbQuery.get_earliest_sell_order_at_price_query().format(price, symbol)
		rows, cols = self._conn.select(query)

		sell_order_id = rows[0][cols.index('order_id')]
		sell_player_id = rows[0][cols.index('player_id')]
		sell_quantity = rows[0][cols.index('quantity')]
		sell_lut = rows[0][cols.index('last_updated_time')]
		
		te = TradeEvent(symbol, self._engine_id, buy_order_id, sell_player_id, buy_quantity, sell_quantity, buy_player_id, sell_player_id, buy_lut, sell_lut, price)
		return te