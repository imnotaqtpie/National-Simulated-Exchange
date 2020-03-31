import time
from enum import Enum

import pandas as pd
import matplotlib.pyplot as plt

class Status(Enum):
    NEWCON = 'New_Confirm'
    MODCON = 'Modify_Confirm'
    CANCON = 'Cancel_Confirm'
    NEWREJ = 'New_Reject'
    MODREJ = 'Modify_Reject'
    CANREJ = 'Cancel_Reject'

class OrderBook:
    def __init__(self, symbol):
        self._symbol = symbol
        self._order_book = dict()
        self._order_book['BUY'] = pd.DataFrame(columns = ['orderId','time_stamp','quantity','price'])
        self._order_book['SELL'] = pd.DataFrame(columns = ['orderId','time_stamp','quantity','price'])
        self._market_price = []
        self._trans_time = []

    def _get_best_price(self, direction):
        if self._order_book[direction].empty:
            return 0
        return self._order_book[direction].iloc[0,3]
            
    def _updateOrderBook(self):
        self._order_book['BUY'].sort_values(by='price' , inplace=True, ascending=False)
        self._order_book['SELL'].sort_values(by='price', inplace=True)
        self._best_bid = self._get_best_price('BUY')
        self._best_ask = self._get_best_price('SELL')
        
    def _get_ord_idx(self, orderId, direction):
        return self._order_book[direction].index[self._order_book[direction]['orderId'] == orderId].astype(int)[0]
        
    def _delete_zero_quantity(self ,direction):
        i = 0
        while self._order_book[direction].iloc[i,2] == 0:
            self.deleteLimitOrder(self._order_book[direction].iloc[i,0], direction)

    def newLimitOrder(self, orderId, time_stamp, direction, quantity, price):
        self._order_book[direction] = self._order_book[direction].append(pd.Series([orderId, time_stamp, quantity, price], index=['orderId','time_stamp','quantity','price']), ignore_index=True)
        self._updateOrderBook()
        
    def modifyLimitOrder(self, orderId, time_stamp, direction, quantity, price):
        if orderId in self._order_book[direction]['orderId'].values:
            idx = self._get_ord_idx(orderId, direction)
            self._order_book[direction].loc[idx] = pd.Series([orderId, time_stamp, quantity, price], index=['orderId','time_stamp','quantity','price'])
        else:
            self.newLimitOrder(orderId, time_stamp, direction, quantity, price)
            if direction == 'BUY':
                self.deleteLimitOrder(orderId, 'SELL')
            else:
                self.deleteLimitOrder(orderId, 'BUY')
        self._updateOrderBook()
        
    def deleteLimitOrder(self, orderId, direction):
        idx = self._get_ord_idx(orderId, direction)
        self._order_book[direction] = self._order_book[direction].drop(idx)
        self._updateOrderBook()
        
    def newMarketOrder(self, orderId, direction, quantity):
        d = "BUY" if direction == "SELL" else "BUY"
        
        if quantity <= self._order_book[d]['quantity'].sum():
            q = quantity
            i = 0
            while q > 0:
                if q > self._order_book[d].iloc[i,2]:                        
                    q -= self._order_book[d].iloc[i,2]
                    self._order_book[d].iloc[i,2] = 0
                else:
                    self._order_book[d].iloc[i,2] -= q
                    q = 0
                i += 1
            self._market_price.append(self._get_best_price(d))
            self._trans_time.append(time.time())

            self._delete_zero_quantity(d)
            return Status.NEWCON
        else:
            return Status.NEWREJ
        
    def _plot_market_movement(self):
        print("\nMarket Prices:",self._market_price)
        plt.plot(self._trans_time, self._market_price,'o')
        plt.xlabel("time")
        plt.ylabel("Stock price")
        plt.show()

    def printOrderBook(self):
        print("\n\t\tOrder Book of ",self._symbol)
        print("\tBest Bid:",self._best_bid,"\t\tBest Ask:",self._best_ask)
        print("BUY Book")
        print(self._order_book['BUY'])
        print("SELL Book")
        print(self._order_book['SELL']) 
        #self._plot_market_movement()
