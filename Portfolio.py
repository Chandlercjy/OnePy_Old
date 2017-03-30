import datetime
import numpy as np
import pandas as pd

from abc import ABCMeta, abstractmethod
from math import floor

from event import FillEvent, OrderEvent, events

from performance import create_sharpe_ratio, create_drawdowns
from performance import *

class Portfolio(object):

    __metaclass__ = ABCMeta

    def __init__(self,events,bars,start_date,initial_capital):
        self.events = events

        self.bars = bars
        self.symbol_list = self.bars.symbol_list

        self.start_date = start_date
        self.initial_capital = initial_capital

        self.log_list = self._construct_log_list()
        self.all_positions = self._construct_all_positions()
        self.current_positions = dict( (k,v) for k,v in [(s,0)
                                                for s in self.log_list])
        self.all_holdings = self._construct_all_holdings()
        self.current_holdings = self._construct_current_holdings()

    @abstractmethod
    def update_signal(self, signalevent):
        raise NotImplementedError('Should implement update_signal()')

    @abstractmethod
    def update_fill(self, fillevent):
        raise NotImplementedError('Should implement update_fill()')

    def _construct_log_list(self):
        d = []
        for i in self.symbol_list:
            l = i + '_long'
            s = i + '_short'
            d.append(l)
            d.append(s)
        return d

class MyPortfolio(Portfolio):
    def __init__(self, bars, start_date='start_date', initial_capital=100000.0):
        super(NaivePortfolio, self).__init__(events,bars,start_date,initial_capital)



class NaivePortfolio(Portfolio):
    def __init__(self, bars, start_date='start_date', initial_capital=100000.0):
        super(NaivePortfolio, self).__init__(events,bars,start_date,initial_capital)

    # private function
    def _construct_all_positions(self):
        d = dict( (k,v) for k, v in [(s, 0) for s in self.log_list])
        d['datetime'] = self.start_date
        return [d]

    def _construct_all_holdings(self):
        d = dict( (k,v) for k,v in [(s,0.0) for s in self.log_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return [d]

    def _construct_current_holdings(self):
        # construct a dict for current holdings
        d = dict( (k,v) for k,v in [(s,0.0) for s in self.log_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital
        return d

    def _update_timeindex(self):
        bars = {}
        for sym in self.symbol_list:
            bars[sym] = self.bars.get_latest_bars(sym, N=1)

        # Update positions
        dp = dict((k,v) for k,v in [(s,0) for s in self.log_list])
        dp['datetime'] = bars[self.symbol_list[0]][0]['date']

        for s in self.log_list:
            dp[s] = self.current_positions[s]

        # Append the current positions
        self.all_positions.append(dp)

        # Update holdings
        dh = dict( (k,v) for k, v in [(s, 0) for s in self.log_list] )
        dh['datetime'] = bars[self.symbol_list[0]][0]['date']
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for s in self.symbol_list:
            # Approximation to the real value
            market_value_l = self.current_positions[s+'_long'] * bars[s][0]['close']
            dh[s+'_long'] = market_value_l

            market_value_s = self.current_positions[s+'_short'] * bars[s][0]['close']
            dh[s+'_short'] = market_value_s

            dh['total'] += market_value_l + market_value_s

        # Append the current holdings
        self.all_holdings.append(dh)

    def _update_positions_from_fill(self, fill):
        """
        Takes a FilltEvent object and updates the position matrix
        to reflect the new position.

        Parameters:
        fill - The FillEvent object to update the positions with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update positions list with new quantities
        # if self.current_holdings['cash'] > fill.quantity*fill.price

        if fill.signal_type == 'LONG' or fill.signal_type == 'EXITLONG':
            self.current_positions[fill.symbol+'_long'] += fill_dir*fill.quantity_l

        # Short is the opposite of long, so -fill_dir
        if fill.signal_type == 'SHORT' or fill.signal_type == 'EXITSHORT':
            self.current_positions[fill.symbol+'_short'] += -fill_dir*fill.quantity_s

        if fill.signal_type == 'EXITALL':
            fill_dir = -1
            self.current_positions[fill.symbol+'_long'] += fill_dir*fill.quantity_l
            self.current_positions[fill.symbol+'_short'] += fill_dir*fill.quantity_s

    def _update_holdings_from_fill(self, fill):
        """
        Takes a FillEvent object and updates the holdings matrix
        to reflect the holdings value.

        Parameters:
        fill - The FillEvent object to update the holdings with.
        """
        # Check whether the fill is a buy or sell
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1

        # Update holdings list with new quantities
        fill_cost = fill.price  # Close price

        if fill.signal_type == 'LONG' or fill.signal_type == 'EXITLONG':
            cost = fill_dir * fill_cost * fill.quantity_l
            self.current_holdings[fill.symbol+'_long'] += cost

        # Short is the opposite of long, so -fill_dir
        if fill.signal_type == 'SHORT' or fill.signal_type == 'EXITSHORT':
            cost = fill_dir * fill_cost * fill.quantity_s
            self.current_holdings[fill.symbol+'_short'] += cost

        if fill.signal_type == 'EXITALL':
            fill_dir = -1
            cost_l = fill_dir * fill_cost * fill.quantity_l
            cost_s = fill_dir * fill_cost * fill.quantity_s
            self.current_holdings[fill.symbol+'_long'] += cost_l
            self.current_holdings[fill.symbol+'_short'] += cost_s

        # Update holdings list with new quantities
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)

    def update_fill(self, fillevent):
        """
        Updates the portfolio current positions and holdings
        from a FillEvent.
        """
        # if fillevent.type == 'Fill':
        if (self.current_holdings['cash'] > fillevent.quantity_l*fillevent.price and
            self.current_holdings['cash'] > fillevent.quantity_s*fillevent.price):
        # print fillevent.price
            self._update_positions_from_fill(fillevent)
            self._update_holdings_from_fill(fillevent)


    def _generate_naive_order(self, signal):
        """
        Simply transacts an OrderEvent object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The SignalEvent signal information.
        """
        order = None

        symbol = signal.symbol
        signal_type = signal.signal_type
        strength = signal.strength
        dt = signal.datetime
        price = signal.price

        mkt_quantity = floor(100 * strength)
        cur_quantity_l = self.current_positions[symbol+'_long']
        cur_quantity_s = self.current_positions[symbol+'_short']
        order_type = 'MKT'

        if signal_type == 'LONG':
            order = OrderEvent(dt, signal_type, symbol, price,
                               order_type,
                               quantity_l = mkt_quantity,
                               quantity_s = 0,
                               direction = 'BUY')
        if signal_type == 'SHORT':
            order = OrderEvent (dt, signal_type, symbol,price,
                                order_type,
                                quantity_l = 0,
                                quantity_s = mkt_quantity,
                                direction = 'SELL')

        if signal_type == 'EXITLONG' and cur_quantity_l > 0:
            order = OrderEvent(dt, signal_type, symbol,price,
                               order_type,
                               quantity_l = mkt_quantity,
                               quantity_s = 0,
                               direction = 'SELL')

        if signal_type == 'EXITSHORT' and cur_quantity_s > 0:
            order = OrderEvent(dt, signal_type, symbol, price,
                               order_type, mkt_quantity,
                               direction = 'BUY')


        # ALL LONG
        if signal_type == 'EXITALL':
            if cur_quantity_l > 0 and cur_quantity_s == 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = cur_quantity_l,
                                   quantity_s = 0,
                                   direction = 'SELL')
        # ALL SHORT
        if signal_type == 'EXITALL':
            if cur_quantity_s > 0 and cur_quantity_l == 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = 0,
                                   quantity_s = cur_quantity_s,
                                   direction = 'BUY')
        # SHORT & LONG
        if signal_type == 'EXITALL':
            if cur_quantity_s > 0 and cur_quantity_l > 0:
                order = OrderEvent(dt, signal_type, symbol, price,
                                   order_type,
                                   quantity_l = cur_quantity_l,
                                   quantity_s = cur_quantity_s,
                                   direction = 'BUY&SELL')

        return order

    def update_signal(self, signalevent):
        if signalevent.type == 'Signal':
            order_event = self._generate_naive_order(signalevent)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        max_dd, dd_duration = create_drawdowns(pnl)

        stats = [('Total Return', '%0.2f%%' % ((total_return - 1.0) * 100.0)),
                 ('sharpe Ratio', '%0.2f' % sharpe_ratio),
                 ('Max Drawdown', '%0.2f%%' % (max_dd * 100.0)),
                 ('Drawdown Duration', '%s' % dd_duration)]
        return stats
