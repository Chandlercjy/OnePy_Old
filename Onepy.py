from Portfolio import *
from feed import *
# import execution
from strategy import *
from execution import *
from event import events
import Queue

from pandas import DataFrame



class OnePiece():
    def __init__(self, data, strategy, portfolio):
        self.events = events
        self.Feed = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.order = SimulatedExecutionHandler(events)

        self._activate = {}

    def sunny(self):
        while True:
            try:
                event = self.events.get(False)
            except Queue.Empty:
                self.Feed.update_bars()
                self.portfolio._update_timeindex()
            else:
                if event is not None:
                    if event.type == 'Market':
                        self.strategy.calculate_signals()

                    if event.type == 'Signal':
                        self.portfolio.update_signal(event)

                    if event.type == 'Order':
                        self.order.execute_order(event)

                        # print order
                        if self._activate['print_order']:
                            event.print_order()

                    if event.type == 'Fill':
                        self.portfolio.update_fill(event)
                        if self._activate['print_order']:
                            event.print_executed()

                if self.Feed.continue_backtest == False:
                    print 'Here is your One Piece!'
                    break

    def print_trade(self):
        self._activate['print_order'] = True


    # get from portfolio
    def get_current_holdings(self):
        return self.portfolio.current_holdings

    def get_current_positions(self):
        return self.portfolio.current_positions

    def get_all_holdings(self):
        return self.portfolio.all_holdings

    def get_all_positions(self):
        return self.portfolio.all_positions

    def get_symbol_list(self):
        return self.portfolio.symbol_list

    def get_initial_capital(self):
        return self.portfolio.initial_capital
