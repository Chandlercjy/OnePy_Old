import datetime
import numpy as np
import pandas as pd
import Queue

from abc import ABCMeta, abstractmethod

from event import SignalEvent

class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplemented('Should implement calculate_signals()')

class BuyAndHoldStrategy(Strategy):
    def __init__(self, bars, events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events

        # Once buy & hold signal is given, these are set to True
        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
            return bought

    def calculate_signals(self, event):
        if event.type == 'Market':
            for s in self.symbol_list:
                bar = self.bars.get_latest_bars(s, N=1)
                if bar is not None and bar !=[]:
                    if self.bought[s] == False:
                        #(Symbol, Datetime, Type = long, short or exit)
                        signal = SignalEvent(bar[0][0], bar[0][1], 'LONG')
                        self.events.put(signal)
                        self.bought[s] = True
