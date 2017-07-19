#coding=utf-8

import talib.abstract as tb
import pandas as pd
import OnePy as op
import itertools

class MyStrategy(op.Strategy):
    def __init__(self,bars,p_list):
        super(MyStrategy,self).__init__(bars)
        self.sma1, \
        self.sma2 = p_list

    def luffy(self):
        for s in self.symbol_list:
            df = self.get_df(s)

            sma1=op.indicator(tb.SMA, 'sma5', df, self.sma1, select=[-1])
            sma2=op.indicator(tb.SMA, 'sma10', df, self.sma2, select=[-1])

            if sma1 > sma2:
                self.long(s,strength=2,percent=True,risky=True)
#                 self.short(s,risky=True)
            if sma1 < sma2:
                self.exitall(s)
#                 self.exitshort(s)
#                 self.exitall(s)
#                 self.long(s)#,strength=2,percent=True,risky=True)

datapath = ''   # 请将datapath输入为000001.csv的文件存放路径

df = pd.read_csv(datapath, index_col=0, parse_dates=True)
symbol_list = ['000001']
data = op.DataFrame_reader(df, symbol_list,start='2015-02-10')
strategy = MyStrategy(data,[5,15])
portfolio = op.NaivePortfolio(data,initial_capital=200000)
go = op.OnePiece(data, strategy, portfolio)


go.print_trade()
go.set_commission=2
go.print_stats()
go.sunny()

# p_sma1=range(5,15)
# p_sma2=range(20,30)
# ppp = op.params_generator(p_sma1,p_sma2)
# op.optimizer(MyStrategy,op.NaivePortfolio,data,ppp)
