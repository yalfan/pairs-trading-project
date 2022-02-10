from query_data import *
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG


class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 10
    n2 = 50

    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        # If sma1 crosses above sma2, close any existing
        # short trades, and buy the asset
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


def backtest(df):
    bt = Backtest(df, SmaCross,
                  cash=100000,
                  exclusive_orders=True)

    output = bt.run()
    bt.plot()
    return output


d1 = "2016-12-6"
d2 = "2021-6-6"

df = get_data_dataframe(d1, d2, "Bitcoin")

bt = Backtest(df, SmaCross,
              cash=100000,
              exclusive_orders=True)

output = bt.run()
print(output)
# bt.plot()
