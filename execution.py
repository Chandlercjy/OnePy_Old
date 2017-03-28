import datetime
import Queue

from abc import ABCMeta, abstractmethod

from event import FillEvent, OrderEvent

class ExecutionHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self,event):
        raise NotImplemented('Should implement execute_order()')

class SimulatedExecutionHandler(ExecutionHandler):
    def __init__(self,events):
        self.events = events

    def execute_order(self,event):
        if event.type == 'Order':
            fill_event = FillEvent(datetime.datetime.utcnow(), event.symbol,
                                  'ARCA', event.quantity, event.direction, None)
            self.events.put(fill_event)
