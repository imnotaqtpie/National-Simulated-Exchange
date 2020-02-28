class ExchangeDbQuery:
	@staticmethod
	def fetch_player_id_query():
		query = "select player_id from players;"
		return query

	@staticmethod
	def fetch_symbols_from_db_query():
		query = "select symbol_id from symbols;"
		return query

	@staticmethod
	def fetch_order_from_db_query():
		query = "select symbol_id, price, quantity from orders where order_id = '{}';"
		return query

	@staticmethod
	def add_order_to_orders_table_query():
		query = "insert into orders (player_id, order_id, symbol_id, price, quantity) values ('{}', '{}', {}, {}, {});"
		return query

	@staticmethod
	def update_order_in_orders_table_query():
		query = "update orders set price = {}, quantity = {} where order_id = '{}';"
		return query

	@staticmethod
	def check_for_table_in_db_query():
		query = "select table_name from INFORMATION_SCHEMA.TABLES where TABLE_NAME = '{}';"
		return query

	@staticmethod
	def create_new_table_for_order_book_query():
		query = "create table {} ( \
					bid_price float, \
					bid_quantity int, \
					ask_price float, \
					ask_quantity int);"
		return query

	@staticmethod
	def clear_order_book_query():
		query = "delete from {};"
		return query

	@staticmethod
	def get_symbol_id_for_name_query():
		query = "select symbol_id from symbols where symbol_name = '{}'"
		return query

	@staticmethod
	def get_all_player_names_query():
		query = "select player_name from players;"
		return query

	@staticmethod
	def insert_new_user_to_db_query():
		query = "insert into players (player_id, player_name) values ('{}', '{}')"
		return query

	@staticmethod
	def get_player_id_for_name_query():
		query = "select player_id from players where player_name = '{}';"
		return query