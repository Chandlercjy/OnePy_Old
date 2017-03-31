import pandas as pd
from execution import SimulatedExecutionHandler
from event import events

import Queue





class OnePiece():
    def __init__(self, data, strategy, portfolio):
        self.events = events
        self.Feed = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.execute = SimulatedExecutionHandler(events)

        self._activate = {}
        self._activate['print_order'] = False

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
                        # print self.Feed.latest_bar_dict['000001'][-1]

                    if event.type == 'Signal':
                        self.portfolio.update_signal(event)
                        # print event.datetime

                    if event.type == 'Order':
                        if (self.portfolio.current_holdings['cash'] > event.quantity_l*event.price and
                            self.portfolio.current_holdings['cash'] > event.quantity_s*event.price):

                            self.execute.execute_order(event)

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

    def get_log(self):
        log = pd.DataFrame(self.portfolio.trade_log)
        return log[['datetime','symbol','signal_type','qty',
                    'cur_positions','cash','total','P/L']]



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
