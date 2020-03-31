class PlayerDbQuery:
	@staticmethod
	def fetch_details_of_symbol_query():
		query = "Select symbol_id, symbol_name, quantity, open_orders from symbols where symbol_name='{}';"
		return query

	@staticmethod
	def fetch_all_symbols_query():
		query = "Select symbol_name from symbols"
		return query

	@staticmethod
	def fetch_details_of_order_query():
		query = "Select symbol_name, quantity, price from order_info where order_id='{}';"
		return query

	@staticmethod
	def update_symbols_db_query():
		query = "Update symbols set quantity = {}, open_orders={} where symbol_name='{}';"
		return query

	@staticmethod
	def update_order_details_into_order_table_query():
		query = "Update order_info set quantity = {}, price = {} where order_id = '{}';"
		return query

	@staticmethod
	def insert_new_symbol_db_query():
		query = "Insert into symbols (symbol_name, quantity, open_orders) values ('{}', {}, {})"
		return query

	@staticmethod
	def insert_order_details_into_order_table_query():
		query = "Insert into order_info (order_id, symbol_name, quantity, price, last_updated_time) values ('{}', '{}', {}, {}, NOW());"
		return query

	@staticmethod
	def remove_order_from_order_table_query():
		query = "delete from order_info where order_id = '{}';"
		return query