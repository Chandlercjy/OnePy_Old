import datetime
import numpy as np
import pandas as pd
import Queue
import math

from abc import ABCMeta, abstractmethod

from event import SignalEvent,events

class Strategy(object):

    __metaclass__ = ABCMeta

    def __init__(self,events,bars):
        self.events = events
        self.bars = bars  # object of feed

        self.symbol_list = self.bars.symbol_list
        self.bar_df_dict = self.bars.bar_df_dict

        self.bought = self._calculate_initial_bought()

        self.bar = None

    @abstractmethod
    def calculate_signals(self):
        raise NotImplemented('Should implement calculate_signals()')

    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
            return bought

    def get_latest_bars(symbol, n=1):
        bar = self.bars.get_latest_bars(symbol, n)
        return bar

    def get_df(symbol):
        return self.bar_df_dict[symbol]

    ############## Order function ##############
    def long(self,symbol,risky=False):
        bar = self.bars.get_latest_bars(symbol, N=1)
        def put():
            if bar is not None and bar !=[]:
                signal = SignalEvent(bar[0][0], bar[0][1], 'LONG')
                self.events.put(signal)

        if not risky:
            if self.bought[symbol] == False:
                if bar is not None and bar !=[]:
                    put()
                    self.bought[symbol] = True
        else:
            put()

    def short(self,symbol,risky=False):
        bar = self.bars.get_latest_bars(symbol, N=1)
        def put():
            if bar is not None and bar !=[]:
                signal = SignalEvent(bar[0][0], bar[0][1], 'SHORT')
                self.events.put(signal)

        if not risky:
            if self.bought[symbol] == False:
                if bar is not None and bar !=[]:
                    put()
                    self.bought[symbol] = True
        else:
            put()

    def exit(self,symbol,risky=False):
        bar = self.bars.get_latest_bars(symbol, N=1)
        def put():
            if bar is not None and bar !=[]:
                signal = SignalEvent(bar[0][0], bar[0][1], 'EXIT')
                self.events.put(signal)

        if not risky:
            if self.bought[symbol] == True:
                if bar is not None and bar !=[]:
                    put()
                    self.bought[symbol] = False
        else:
            put()

    ##################################################

def indicator(ind_func, name, df, timeperiod, select,index=False,signal=True):
    """
    ind_func: function from tablib
    ind_name: name of indicator
    df: DataFrame
    timeperiod: int
    select: list or int.
        - Attention:
            index start from -1, select=[0] or [0,n] is invalid.
    index: default False, if True, select df by index
        - for example:
            select=[1,2] means df.iloc[1:2,:]

    """
    def offset(select):
        if min(select)<0:
            return abs(min(select))
        else:
            return 0
    off = offset(select)

    ori_df = df
    df = df.iloc[-timeperiod-off:,:]
    total_df = pd.DataFrame()
    ind_df = ind_func(df,timeperiod)
    ind_df = pd.DataFrame(ind_df)


    if ori_df.shape[0] < timeperiod:
        return

    def check():
        check = df_selected.empty or math.isnan(df_selected.iat[0,0])
        if check:
            raise SyntaxError ('select NaN values!')


    if index:
        if type(select) is list:
            if len(select) == 1:
                df_selected = ind_df.iloc[select[0]:,:]
            else:
                i = select[0]
                j = select[1]
                df_selected = ind_df.iloc[i:j,:]

            check()
            total_df = total_df.append(df_selected)
        else:
            print 'Params select wrong! Maybe out of range or something'
    else:
        if type(select) is list:
            for i in select:
                if i >= 0:
                    df_selected = ind_df.iloc[i:i+1,:]
                if i == -1:
                    df_selected = ind_df.iloc[-1:,:]
                if i < -1:
                    df_selected = ind_df.iloc[i-1:i,:]

                check()
                total_df = total_df.append(df_selected)
        else:
            print 'Params select wrong! Maybe out of range or something'

    total_df.rename(columns={total_df.columns[0]:name},inplace=True)

    if index:
        return total_df
    if signal:
        return total_df.iat[0,0]
    else:
        return total_df

################ Strategy ####################
from talib.abstract import *
class SMAStrategy(Strategy):
    def __init__(self,bars):
        super(SMAStrategy,self).__init__(events,bars)

    def calculate_signals(self):
        df = self.bar_df_dict['000001'][['close']]

        sma5=indicator(SMA, 'sma5', df, 5, select=[-1])
        sma10=indicator(SMA, 'sma10', df, 10, select=[-1])
        if sma5 > sma10:
            self.long('000001')#,risky=True)
        if sma5 < sma10:
            self.exit('000001')#,risky=True)



class BuyAndHoldStrategy(Strategy):
    def __init__(self,bars):
        super(BuyAndHoldStrategy,self).__init__(events,bars)

    def calculate_signals(self):
        # if event.type == 'Market':
        self.long('000001')
