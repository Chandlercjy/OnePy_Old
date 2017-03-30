import numpy as np
import pandas as pd

def create_sharpe_ratio(returns, periods=252):
    """
    Create the Sharpe ratio for the strategy, based on a
    benchmark of zero (i.e. no risk-free rate information).

    Parameters:
    returns - A pandas Series representing period percentage returns.
    periods - Daily (252), Hourly (252*6.5), Minutely(252*6.5*60) etc.
    """
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(equity_curve):
    """
    Calculate the largest peak-to-trough drawdown of the PnL curve
    as well as the duration of the drawdown. Requires that the
    pnl_returns is a pandas Series.

    Parameters:
    pnl - A pandas Series representing period percentage returns.

    Returns:
    drawdown, duration - Highest peak-to-trough drawdown and duration.
    """

    # Calculate the cumulative returns curve
    # and set up the High Water Mark
    # Then create the drawdown and duration series
    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index = eq_idx)
    duration = pd.Series(index = eq_idx)

    # Loop over the index range
    for t in range(1, len(eq_idx)):
        cur_hwm = max(hwm[t-1], equity_curve[t])
        hwm.append(cur_hwm)
        drawdown[t]= hwm[t] - equity_curve[t]
        duration[t]= 0 if drawdown[t] == 0 else duration[t-1] + 1
    return drawdown.max(), duration.max()


class TradeLog():
    """ trade log """

    def __init__(self):
        columns = ['entry_date', 'entry_price', 'long_short', 'qty',
                   'exit_date', 'exit_price', 'pl_points', 'pl_cash',
                   'cumul_total']
        self._tlog = pd.DataFrame(columns=columns)
        self.shares = 0

    def calc_shares(self, cash, price):
        """ calculate shares and remaining cash before entry """
        shares = int(cash / price)
        cash = cash - shares*price
        return shares, cash

    def calc_shares2(self, cash, price):
        """ calculate shares and remaining cash before entry """
        shares = 100
        cash = cash - shares*price
        return shares, cash

    def calc_cash(self, cash, price, shares):
        """ calculate cash after exit """
        cash = cash + price*shares
        return cash

    def enter_trade(self, entry_date, entry_price, shares, long_short='long'):
        """ record trade entry in trade log """
        d = {'entry_date':entry_date, 'entry_price':entry_price, 'qty':shares,
             'long_short':long_short}
        tmp = pd.DataFrame([d], columns=self._tlog.columns)
        self._tlog = self._tlog.append(tmp, ignore_index=True)

        # update shares
        if long_short == 'long':
            self.shares += shares
        else:
            self.shares -=shares

    def _get_open_trades(self):
        """ find the "integer" index of rows with NaN """
        return pd.isnull(self._tlog).any(1).nonzero()[0]

    def num_open_trades(self):
        """ return number of open orders, i.e. not closed out """
        return len(self._get_open_trades())

    def exit_trade(self, exit_date, exit_price, shares=-1, long_short='long'):
        """ record trade exit in trade log """

        rows = self._get_open_trades()
        idx = rows[0]

        entry_price = self._tlog['entry_price'][idx]
        shares = self._tlog['qty'][idx] if shares == -1 else shares
        pl_points = exit_price - entry_price
        pl_cash = pl_points * shares
        if idx == 0:
            cumul_total = pl_cash
        else:
            cumul_total = self._tlog.ix[idx - 1, 'cumul_total'] + pl_cash

        self._tlog.ix[idx, 'exit_date'] = exit_date
        self._tlog.ix[idx, 'exit_price'] = exit_price
        self._tlog.ix[idx, 'long_short'] = 'long'
        self._tlog.ix[idx, 'pl_points'] = pl_points
        self._tlog.ix[idx, 'pl_cash'] = pl_cash
        self._tlog.ix[idx, 'cumul_total'] = cumul_total

        # update shares
        if long_short == 'long':
            self.shares -= shares
        else:
            self.shares +=shares
        return idx

    def get_log(self):
        """ return Dataframe """
        return self._tlog
