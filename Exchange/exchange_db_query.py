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
	def update_order_in_orders_table_without_changing_time_query():
		query = "update orders set price = {}, quantity = {}, last_updated_time = '{}' where order_id = '{}';"
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

	@staticmethod
	def get_all_symbol_details_query():
		query = "select symbol_id, symbol_name from symbols;"
		return query

	@staticmethod
	def delete_order_in_orders_table_query():
		query = "delete from orders where order_id = '{}';"
		return query

	@staticmethod
	def get_all_info_of_order_query():
		query = "select order_id, symbol_id, price, quantity, player_id, last_updated_time from orders where order_id = '{}';"
		return query

	@staticmethod
	def update_or_insert_order_book_entry_into_db_query():
		query = "insert into {} (price, quantity) values ({}, {}) \
		on conflict on constraint {}_pkey do update set quantity = {} where {}.price = {};"
		return query

	@staticmethod
	def get_top_level_order_book_data_query():
		query = "select * from {0}_short inner join {0}_long on {0}_short.price <= {0}_long.price order by {0}_long.price desc;"
		return query

	@staticmethod
	def get_earliest_buy_order_at_price_query():
		query = "select * from orders where price = {} and symbol_id = {} and quantity > 0 order by last_updated_time desc limit 1;"
		return query

	@staticmethod
	def get_earliest_sell_order_at_price_query():
		query = "select * from orders where price = {} and symbol_id = {} and quantity < 0 order by last_updated_time desc limit 1;"
		return query

	@staticmethod
	def delete_order_book_entry_from_db_query():
		query = "delete from {} where price = {};"
		return query

	@staticmethod
	def get_all_player_details_query():
		query = "select player_id, player_name from players;"
		return query