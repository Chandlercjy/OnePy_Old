from Portfolio import *
from feed import *
# import execution
from strategy import *
from execution import *
from event import events
import Queue



class OnePiece():
    def __init__(self, data, strategy, portfolio):
        self.events = events
        self.Feed = data
        self.strategy = strategy
        self.portfolio = portfolio
        self.order = SimulatedExecutionHandler(events)

    def sunny(self):
        while True:
            try:
                event = self.events.get(False)
            except Queue.Empty:
                self.Feed.update_bars()
            else:
                if event is not None:
                    if event.type == 'Market':
                        self.strategy.calculate_signals(event)

                    if event.type == 'Signal':
                        self.portfolio.update_signal(event)

                    if event.type == 'Order':
                        self.order.execute_order(event)
                        event.print_order()

                    if event.type == 'Fill':
                        self.portfolio.update_fill(event)
                        self.portfolio.update_timeindex(event)

                if self.Feed.continue_backtest == False:
                    print 'over'
                    break
