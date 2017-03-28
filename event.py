class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self):
        self.type = 'Market'
        # print 'here is a marketevent'

class SignalEvent(Event):
    def __init__(self, symbol, datetime, signal_type):
        self.type = 'Signal'
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strength = 1  # control the amount of positions


class OrderEvent(Event):
    def __init__(self, symbol, order_type, quantity, direction):
        self.type = 'Order'
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        print "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            (self.symbol, self.order_type, self.quantity, self.direction)

class FillEvent(Event):
    def __init__(self, timeindex, symbol, exchange, quantity,
                 direction, fill_cost, commission=None):
        self.type = 'Fill'
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_cost = fill_cost

        # Calculate commission
        if  commission is None:
            self.commission = 0
        else:
            self.commission = commission
