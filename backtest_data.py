import pandas as pd

from query_data import *
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from typing import Sequence, Optional, Union, Callable
from numbers import Number
from backtesting.test import SMA, GOOG

from pandas_datareader import data as pdr


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


def STD_DEV(arr: pd.Series, n: int):
    return pd.Series(arr).rolling(n).std()


def RATIO(arr: pd.Series):
    return pd.Series(arr)


def Z_SCORE(arr: pd.Series):
    return pd.Series(arr)


def INDICATOR(arr: pd.Series):
    return arr


class PairRatio(Strategy):
    def init(self):
        self.entry = 2
        self.exit = 0
        self.downtick = 0
        self.max = 5
        self.ma_period = 15
        self.type = "exponential"
        self.std_period = 15
        self.entry_mode = "uptick"
        self.rsi_period = 14
        self.rsi_threshold = 0
        self.ratio = self.I(INDICATOR, self.data.Ratio)
        self.sma = self.I(INDICATOR, self.data.SMA)
        self.std_dev = self.I(INDICATOR, self.data.STD)
        self.z_score = self.I(INDICATOR, self.data.Z_SCORE)
        self.lom = self.data.LoM[0]  # less or more
        self.dates = self.I(INDICATOR, self.data.index)
        # print(self.data.index)
        # print(self.z_score[290:320])
        # print("ratio", self.ratio)
        # print("sma", self.sma)
        # print("std dev", self.std_dev)
        # print("z-score", self.z_score)

    def entry_threshold(self, series1: Sequence, entry):
        z_scores = (
            series1.values if isinstance(series1, pd.Series) else
            (series1, series1) if isinstance(series1, Number) else
            series1)

        # if ratio = small/big (<1) and z > entry, short small, long big
        # if ratio = small/big (<1) and z < -entry, long small, short big

        if self.ratio < 1 and self.lom == "Less":
            if z_scores[-1] > entry:
                return "Short"
            if z_scores[-1] < -entry:
                return "Long"

        if self.ratio < 1 and self.lom == "More":
            if z_scores[-1] > entry:
                return "Long"
            if z_scores[-1] < -entry:
                return "Short"

        # if ratio = big/small (>1) and z > entry, long small, short big
        # if ratio = big/small (>1) and z < -entry, short small, long big
        if self.ratio > 1 and self.lom == "Less":
            if z_scores[-1] > entry:
                return "Long"
            if z_scores[-1] < -entry:
                return "Short"

        if self.ratio > 1 and self.lom == "More":
            if z_scores[-1] > entry:
                return "Short"
            if z_scores[-1] < -entry:
                return "Long"

        if abs(z_scores[-1]) < 0.5:
            return "Close"

    def next(self):
        action = self.entry_threshold(self.z_score, self.entry)
        if action == "Short" and self.position.size == 0:
            # print(self.z_score[-1])
            # print(self.dates[-1])
            self.sell()
        if action == "Long" and self.position.size == 0:
            # print(self.z_score[-1])
            # print(self.dates[-1])
            self.buy()
        if action == "Close" and abs(self.position.size) > 0:
            self.position.close()
            # print(self.z_score[-1])
            # print(self.dates[-1])
            # print("Close!")


def backtest_data(df1, df2):
    ratio = ((df1 / df2)['Close']).rename("Ratio")
    sma = SMA(ratio, 15).rename("SMA")
    std_dev = STD_DEV(ratio, 15).rename("STD")
    z_score = pd.Series((ratio - sma) / std_dev).rename("Z_SCORE")

    if df1['Open'][0] > df2['Open'][0]:
        more = ratio.rename('LoM')
        more[0] = 'More'
        df1_combined = pd.concat([df1, ratio, sma, std_dev, z_score, more], axis=1, ignore_index=False)
        less = ratio.rename('LoM')
        less[0] = 'Less'
        df2_combined = pd.concat([df2, ratio, sma, std_dev, z_score, less], axis=1, join='inner')
    else:
        less = ratio.rename('LoM')
        less[0] = 'Less'
        df1_combined = pd.concat([df1, ratio, sma, std_dev, z_score, less], axis=1, join='inner')
        more = ratio.rename('LoM')
        more[0] = 'More'
        df2_combined = pd.concat([df2, ratio, sma, std_dev, z_score, more], axis=1, join='inner')

    bt_df1 = Backtest(df1_combined, PairRatio, cash=100000, exclusive_orders=True)
    bt_df2 = Backtest(df2_combined, PairRatio, cash=100000, exclusive_orders=True)

    output_df1 = bt_df1.run()
    output_df2 = bt_df2.run()
    return output_df1, output_df2


def get_trades(trades):
    names, size, entry_price, exit_price, pnl, entry_time, exit_time = [], [], [], [], [], [], []
    for index, row in trades.iterrows():
        names.append(row['Name'])
        size.append(row['Size'])
        entry_price.append(row['EntryPrice'])
        exit_price.append(row['ExitPrice'])
        pnl.append(row['PnL'])
        entry_time.append(row['EntryTime'])
        exit_time.append(row['ExitTime'])
    return names, size, entry_price, exit_price, pnl, entry_time, exit_time


def combine_trades(tuple1, tuple2):
    combined_name = unzip(zip(tuple1[0], tuple2[0]))
    combined_size = unzip(zip(tuple1[1], tuple2[1]))
    combined_entry_price = unzip(zip(tuple1[2], tuple2[2]))
    combined_exit_price = unzip(zip(tuple1[3], tuple2[3]))
    combined_pnl = unzip(zip(tuple1[4], tuple2[4]))
    combined_entry_time = unzip(zip(tuple1[5], tuple2[5]))
    combined_exit_time = unzip(zip(tuple1[6], tuple2[6]))
    arr = np.array([combined_name, combined_size, combined_entry_price, combined_exit_price, combined_pnl, combined_entry_time, combined_exit_time], dtype=object)
    arr = arr.T
    df = pd.DataFrame(arr,  columns=['Name', 'Size', 'Entry Price', 'Exit Price', 'PnL', 'Entry Time', 'Exit Time'])
    return df


def unzip(arr):
    new_arr = []
    for i in arr:
        for j in i:
            new_arr.append(j)
    return new_arr


def create_names(name, length):
    names = [None] * length
    for i in range(len(names)):
        names[i] = name
    return pd.Series(names)

