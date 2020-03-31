from db_connector import DbConnector 

conn = DbConnector('postgres', 5432, 'postgres', '127.0.0.1')
print(conn._cursor)
rows, cols = conn.select("select * from symbols;")

print(rows[0][cols.index('quantity')], cols)