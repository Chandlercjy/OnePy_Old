import datetime
import numpy as np
import pandas as pd
import Queue

from abc import ABCMeta, abstractmethod

from event import SignalEvent,events

class Strategy(object):

    __metaclass__ = ABCMeta

    def __init__(self,events,bars):
        self.events = events
        self.bars = bars  # object of feed
        self.symbol_list = self.bars.symbol_list
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

    def get_latest_bars(s, n=1):
        bar = self.bars.get_latest_bars(s, n)
        return bar

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

class SMAStrategy(Strategy):
    def __init__(self):
        super(SMAStrategy,self).__init__(events)



class BuyAndHoldStrategy(Strategy):
    def __init__(self,bars):
        super(BuyAndHoldStrategy,self).__init__(events,bars)


        # Once buy & hold signal is given, these are set to True


    def calculate_signals(self, event):
        if event.type == 'Market':

            self.long('000001', risky=True)

                        # self.bought[s] = True


## Backup
# class BuyAndHoldStrategy(Strategy):
#     def __init__(self, bars):
#         super(BuyAndHoldStrategy,self).__init__(events)
#
#
#         # Once buy & hold signal is given, these are set to True
#         self.bought = self._calculate_initial_bought()
#
#     def _calculate_initial_bought(self):
#         bought = {}
#         for s in self.symbol_list:
#             bought[s] = False
#             return bought
#
#     def calculate_signals(self, event):
#         if event.type == 'Market':
#             for s in self.symbol_list:
#                 bar = self.bars.get_latest_bars(s, N=1)
#                 if bar is not None and bar !=[]:
#                     if self.bought[s] == False:
#                         #(Symbol, Datetime, Type = long, short or exit)
#                         signal = SignalEvent(bar[0][0], bar[0][1], 'LONG')
#                         self.events.put(signal)
#                         # self.long()
#                         self.bought[s] = True
