from Portfolio import *
import feed
import event
# import execution
from strategy import *
from execution import *
import Queue

def run():
    while True:
        Feed.update_bars()
        try:
            event = events.get(False)
        except Queue.Empty:
            pass
        else:
            if event is not None:
                if event.type == 'Market':
                    strategy.calculate_signals(event)

                if event.type == 'Signal':
                    portfolio.update_signal(event)

                if event.type == 'Order':
                    order.execute_order(event)
                    event.print_order()

                if event.type == 'Fill':
                    portfolio.update_fill(event)
                    portfolio.update_timeindex(event)

            if Feed.continue_backtest == False:
                print 'over'
                break

events = Queue.Queue()
Feed = feed.CSV_tushare_stock(events, '/Users/chandler/Desktop/000001.csv', '000001')
strategy = BuyAndHoldStrategy(Feed, events)
start_date = '2017-01-01'
portfolio = NaivePortfolio(Feed, events, start_date)
order = SimulatedExecutionHandler(events)

run()
