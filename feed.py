import datetime
import os, os.path
import pandas as pd

from abc import ABCMeta, abstractmethod
from event import MarketEvent,events

class DataHandler(object):

    __metaclass__ = ABCMeta

    def __init__(self,events):
        self.events = events

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError("Should implement update_bars()")

class CSV_tushare_stock(DataHandler):
    def __init__(self, csv_path, symbol):

        super(CSV_tushare_stock, self).__init__(events)

        self.csv_path = csv_path
        self.symbol = symbol   # str

        self.symbol_list = []  # stock code list
        self.symbol_list.append(symbol)

        self.symbol_dict = {}   # a dict contain DataFrames
        self.latest_bar_dict = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

        roll_data=None
        self.roll_data = roll_data  # for generator

    def _open_convert_csv_files(self):
        comb_index = None
        s = self.symbol
        # Load the CSV and set index to Datatime
        symbol_data = pd.read_csv(self.csv_path, index_col=0)
        symbol_data.index = symbol_data['date']
        symbol_data.drop('date', axis=1, inplace=True)
        symbol_data.index = pd.DatetimeIndex(symbol_data.index)
        self.symbol_dict[s] = symbol_data
        # Combine the index to pad forward values, depreciated for now!!!
        if comb_index is None:
            comb_index = self.symbol_dict[s].index
        else:
            comb_index = comb_index.union(self.symbol_dict[s].index)

        # Create and Set the lates symbol_dict to None
        self.latest_bar_dict[s] = []

        # Reindex the DataFrames, depreciated for now!!!
        self.symbol_dict[s] = self.symbol_dict[s].reindex(
                                    index=comb_index,method='pad'
                                    )

    def _get_new_bar(self, symbol):
        """
        Returns the latest bar from the data feed as a tuple of
        (sybmbol, datetime, open, low, high, close, volume, code).

        yield also create a generator
        """
        df = self.symbol_dict[symbol]
        lenth = len(df)
        for i in range(lenth):
            yield tuple([symbol, str(df.index[i]),
                                 df.iat[i,0], df.iat[i,3],
                                 df.iat[i,2], df.iat[i,1],
                                 df.iat[i,4], df.iat[i,5]])

    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_bar_dict[symbol]
        except KeyError:
            print "That symbol is not available in the historical data set."
        else:
            return bars_list[-N:]


    def update_bars(self):
        """
        Everytime update, update bar from the 0 row for every symbol
        run strategy one by one for all symbol,
        need a event loop
        and finally fullfill the latest_bar_dict
        """
        if self.latest_bar_dict[self.symbol] == [] :
            self.roll_data = self._get_new_bar(self.symbol)
        try:
            bar = self.roll_data.next()
        except StopIteration:
            self.continue_backtest = False
        else:
            if bar is not None:
                self.latest_bar_dict[self.symbol].append(bar)
        self.events.put(MarketEvent())
