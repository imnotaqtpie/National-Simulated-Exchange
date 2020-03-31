import time
from order_book import OrderBook

obj = OrderBook('AAPL')

obj.newLimitOrder(1, time.ctime(time.time()), 'BUY', 100, 50.0)
time.sleep(1)
obj.newLimitOrder(2, time.ctime(time.time()), 'BUY', 400, 10.0)
obj.newLimitOrder(3, time.ctime(time.time()), 'SELL', 100, 90.0)
time.sleep(1)
obj.newLimitOrder(4, time.ctime(time.time()), 'BUY', 300, 50.0)
obj.newLimitOrder(5, time.ctime(time.time()), 'SELL', 100, 40.0)

obj.printOrderBook()
obj.modifyLimitOrder(4, time.ctime(time.time()), 'BUY', 400, 40)
obj.printOrderBook()
obj.modifyLimitOrder(4, time.ctime(time.time()), 'SELL', 300, 30)
print(obj.newMarketOrder(6, 'SELL', 150))
time.sleep(1)
obj.printOrderBook()
print(obj.newMarketOrder(7, 'SELL', 250))
time.sleep(1)
obj.printOrderBook()
print(obj.newMarketOrder(8, 'SELL', 250))
obj.printOrderBook()