import pandas as pd

from query_data import *


def SMA(arr: pd.Series, n: int):
    return pd.Series(arr).rolling(n).mean()


def STD_DEV(arr: pd.Series, n: int):
    return pd.Series(arr).rolling(n).std()


def RATIO(arr: pd.Series):
    return pd.Series(arr)


def Z_SCORE(arr: pd.Series):
    return pd.Series(arr)


class PairRatio():
    def __init__(self, ratio, sma, std_dev, z_score, df1, df2, equity, params):
        ma_period, std_period, max_dur, entry_threshold, exit_threshold, sl_threshold = \
            params[0], params[1], params[2], params[3], params[4], params[5]
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.exit = 0
        self.downtick = 0
        self.max = 5
        self.ma_period = 15
        self.type = "exponential"
        self.std_period = 15
        self.entry_threshold_mode = "uptick"
        self.rsi_period = 14
        self.rsi_threshold = 0
        self.ratio = ratio
        self.sma = sma
        self.std_dev = std_dev
        self.z_scores = z_score
        self.dates = df1.index
        self.trades = []
        self.open_position = False
        self.position = []
        self.prices1 = df1['Close']
        self.prices2 = df2['Close']
        self.coin1 = df1.name
        self.coin2 = df2.name
        self.df1 = df1
        self.df2 = df2
        self.i = 0
        self.equity = equity
        self.portfolio = 0
        self.portfolio_values = []
        self.today = datetime.datetime.today().date()
        self.lom = {
            self.coin1: "Less" if self.prices1[0] < self.prices2[0] else "More",
            self.coin2: "Less" if self.prices2[0] < self.prices1[0] else "More"
        }
        self.coins = {
            self.coin1: self.df1,
            self.coin2: self.df2
        }

    def run(self):
        for i in range(len(self.dates)):
            self.i = i
            # print(self.equity)
            if not self.open_position:
                action = self.get_action(self.coin1)
                if action == "Short":
                    self.short_long(self.coin1, self.coin2)
                if action == "Long":
                    self.long_short(self.coin1, self.coin2)
            elif self.open_position:
                action = self.get_action(self.coin1)
                if action == "Close":
                    self.close()
            if self.dates[i].date() == self.today and self.open_position:
                self.close()
            self.update_portfolio()

    def short_long(self, coin1, coin2):
        vals1, vals2 = self.coins.get(coin1), self.coins.get(coin2)
        prices1, prices2 = vals1['Close'], vals2['Close']
        value = 0.5 * self.equity  # Divide the cash equally

        # print(self.portfolio_values)
        # x = int(value / (prices1[self.i]))  # Find the number of shares for Stock1
        # y = int(value / (prices2[self.i]))  # Find the number of shares for Stock2
        x = round((value / (prices1[self.i])), 2)  # Find the number of shares for Stock1
        y = round((value / (prices2[self.i])), 2)  # Find the number of shares for Stock2
        position1 = Position(self.dates[self.i], prices1[self.i], x, "Short", coin1, self.z_scores[self.i])  # Short coin1
        position2 = Position(self.dates[self.i], prices2[self.i], y, "Long", coin2, self.z_scores[self.i])  # Long coin2
        self.equity = self.equity + x * self.prices1[self.i] - y * self.prices2[self.i]  # add short, subtract long
        self.trades.append([position1, position2])
        self.position.extend([position1, position2])
        self.open_position = True
        # print("short long: ", self.equity)

    def long_short(self, coin1, coin2):
        vals1, vals2 = self.coins.get(coin1), self.coins.get(coin2)
        prices1, prices2 = vals1['Close'], vals2['Close']
        value = 0.5 * self.equity  # Divide the cash equally

        # print(self.portfolio_values)
        # x = int(value / (prices1[self.i]))  # Find the number of shares for Stock1
        # y = int(value / (prices2[self.i]))  # Find the number of shares for Stock2
        x = round((value / (prices1[self.i])), 2)  # Find the number of shares for Stock1
        y = round((value / (prices2[self.i])), 2)  # Find the number of shares for Stock2
        position1 = Position(self.dates[self.i], prices1[self.i], x, "Long", coin1, self.z_scores[self.i])  # Long coin1
        position2 = Position(self.dates[self.i], prices2[self.i], y, "Short", coin2, self.z_scores[self.i])  # Short coin2
        self.equity = self.equity - x * self.prices1[self.i] + y * self.prices2[self.i]  # add short, subtract long
        self.trades.append([position1, position2])
        self.position.extend([position1, position2])
        self.open_position = True
        # print("long short: ", self.equity)

    def long(self, coin1):
        vals1 = self.coins.get(coin1)
        prices1 = vals1['Close']
        value = self.equity  # Divide the cash equally

        # print(self.portfolio_values)
        x = int(value / (prices1[self.i]))  # Find the number of shares for Stock1
        position1 = Position(self.dates[self.i], prices1[self.i], x, "Long", coin1, self.z_scores[self.i])  # Long coin1
        self.equity = self.equity - x * self.prices1[self.i]  # subtract long
        self.trades.append([position1])
        self.position.extend([position1])
        self.open_position = True
        # print("long short: ", self.equity)

    def short(self, coin1):
        vals1 = self.coins.get(coin1)
        prices1 = vals1['Close']
        value = self.equity  # Divide the cash equally

        # print(self.portfolio_values)
        x = int(value / (prices1[self.i]))  # Find the number of shares for Stock1
        position1 = Position(self.dates[self.i], prices1[self.i], x, "Long", coin1, self.z_scores[self.i])  # Long coin1
        self.equity = self.equity + x * self.prices1[self.i]  # subtract long
        self.trades.append([position1])
        self.position.extend([position1])
        self.open_position = True
        # print("long short: ", self.equity)

    def close(self):
        pos1, pos2 = self.position[0], self.position[1]
        self.close_long(pos1) if pos1.type == "Long" else self.close_short(pos1)
        self.close_long(pos2) if pos2.type == "Long" else self.close_short(pos2)
        self.update_positions()
        # print("after close: ", self.equity)

    def close_long(self, pos):
        # print(self.equity, pos.quantity, self.coins.get(pos.coin)['Close'][self.i])
        self.portfolio = pos.quantity * self.coins.get(pos.coin)['Close'][self.i]
        self.equity += abs(self.portfolio)

    def close_short(self, pos):
        # print(self.equity, pos.quantity, self.coins.get(pos.coin)['Close'][self.i])
        self.portfolio = pos.quantity * self.coins.get(pos.coin)['Close'][self.i]
        self.equity -= abs(self.portfolio)

    def update_positions(self):
        pt1 = self.trades[-1][0]
        pt2 = self.trades[-1][1]
        pt1.set_close_date(self.dates[self.i])
        pt1.set_close_price(self.coins.get(pt1.coin)['Close'][self.i])
        pt2.set_close_date(self.dates[self.i])
        pt2.set_close_price(self.coins.get(pt2.coin)['Close'][self.i])
        self.position.clear()
        self.open_position = False

    def update_portfolio(self):
        if not self.open_position:
            self.portfolio_values.append(self.equity)
        elif self.open_position:
            c1, c2 = self.position[0], self.position[1]
            # self.update_long(c1) if c1.type == "Long" else self.update_long(c2)
            # self.update_short(c1) if c1.type == "Short" else self.update_short(c2)
            self.update_portfolio_values(c1, c2)

    def update_long(self, coin):
        self.portfolio = coin.quantity * self.coins.get(coin.coin)['Close'][self.i]
        portfolio_value = self.equity + self.portfolio - coin.quantity * coin.price
        self.portfolio_values.append(portfolio_value)

    def update_short(self, coin):
        self.portfolio = coin.quantity * self.coins.get(coin.coin)['Close'][self.i]
        portfolio_value = self.equity - self.portfolio + coin.quantity * coin.price
        self.portfolio_values.append(portfolio_value)

    def update_portfolio_values(self, c1, c2):
        curr1 = c1.quantity * self.coins.get(c1.coin)['Close'][self.i]
        curr2 = c2.quantity * self.coins.get(c2.coin)['Close'][self.i]
        iv1 = c1.quantity * c1.price
        iv2 = c2.quantity * c2.price
        portfolio_value = self.equity + (curr1 - iv1) - (curr2 - iv2) if c1.type == "Long" else \
            self.equity - (curr1 - iv1) + (curr2 - iv2)
        self.portfolio_values.append(portfolio_value)

    def get_action(self, coin):
        lom = self.lom.get(coin)
        # if ratio = small/big (<1) and z > entry_threshold, short small, long big
        # if ratio = small/big (<1) and z < -entry_threshold, long small, short big
        if self.ratio[self.i] < 1 and lom == "Less":
            if self.z_scores[self.i] > self.entry_threshold:
                return "Short"
            if self.z_scores[self.i] < -self.entry_threshold:
                return "Long"

        if self.ratio[self.i] < 1 and lom == "More":
            if self.z_scores[self.i] > self.entry_threshold:
                return "Long"
            if self.z_scores[self.i] < -self.entry_threshold:
                return "Short"

        # if ratio = big/small (>1) and z > entry, long small, short big
        # if ratio = big/small (>1) and z < -entry, short small, long big
        if self.ratio[self.i] > 1 and lom == "Less":
            if self.z_scores[self.i] > self.entry_threshold:
                return "Long"
            if self.z_scores[self.i] < -self.entry_threshold:
                return "Short"

        if self.ratio[self.i] > 1 and lom == "More":
            if self.z_scores[self.i] > self.entry_threshold:
                return "Short"
            if self.z_scores[self.i] < -self.entry_threshold:
                return "Long"

        if abs(self.z_scores[self.i]) < 0.5:
            return "Close"
        return "Nothing"


class Position:
    def __init__(self, date, price, quantity, type, coin, z_score):
        self.date = date
        self.price = price
        self.quantity = quantity
        self.type = type
        self.coin = coin
        self.close_date = date
        self.close_price = price
        self.pnl = 0
        self.z_score = z_score

    def set_close_date(self, close_date):
        self.close_date = close_date

    def set_close_price(self, close_price):
        self.close_price = close_price
        if self.type == "Long":
            self.pnl = self.quantity * self.close_price - self.quantity * self.price
        elif self.type == "Short":
            self.pnl = self.quantity * self.price - self.quantity * self.close_price

    def to_string(self):
        return "Coin: %s, Quantity: %s, Type: %s, Open Date: %s, Close Date: %s, Open Price: %s, Close Price: %s"\
               % (self.coin, self.quantity, self.type, self.date, self.close_date, self.price, self.close_price)


def custom_backtest(df1, df2, params, equity):
    ma_period, std_period, max_dur, entry_threshold, exit_threshold, sl_threshold = \
        params[0], params[1], params[2], params[3], params[4], params[5]
    ratio = (df1['Close'] / df2['Close']).rename("Ratio")
    sma = SMA(ratio, ma_period).rename("SMA")
    std_dev = STD_DEV(ratio, std_period).rename("STD")
    z_score = pd.Series((ratio - sma) / std_dev).rename("Z_SCORE")
    bt = PairRatio(ratio, sma, std_dev, z_score, df1, df2, equity)
    bt.run()
    return bt


"""
Moving average period
standard deviation period
Maximum trading duration
Entry threshold
Exit threshold
Stop/Loss threshold
"""


def get_trades_df(bt):
    names, size, entry_price, exit_price, pnl, entry_time, exit_time, z_score, op = [], [], [], [], [], [], [], [], []
    index = []
    index_num = 1
    for i in bt.trades:
        index.extend([index_num, index_num])
        index_num += 1
        names.extend([i[0].coin, i[1].coin])
        size.extend([i[0].quantity, i[1].quantity])
        entry_price.extend([round(i[0].price, 3), round(i[1].price, 3)])
        exit_price.extend([round(i[0].close_price, 3), round(i[1].close_price, 3)])
        pnl.extend([round(i[0].pnl, 3), round(i[1].pnl, 3)])
        entry_time.extend([i[0].date.strftime('%Y-%m-%d'), i[1].date.strftime('%Y-%m-%d')])
        exit_time.extend([i[0].close_date.strftime('%Y-%m-%d'), i[1].close_date.strftime('%Y-%m-%d')])
        z_score.extend([round(i[0].z_score, 3), round(i[1].z_score, 3)])
        op.extend([i[0].type, i[1].type])

    arr = np.array([index, names, op, entry_time, exit_time, size, entry_price, exit_price, pnl, z_score], dtype=object)
    arr = arr.T
    df = pd.DataFrame(arr,
                      columns=['Index', 'Name', 'Operation', 'Entry Time', 'Exit Time',
                               'Size', 'Entry Price', 'Exit Price', 'PnL', 'Z-Score'])
    return df


def get_equity_curve(bt):
    return bt.portfolio_values


"""out_df1 = get_data_dataframe('2020-06-06', '2021-06-06', 'Bitcoin')
out_df1.name = "Bitcoin"

out_df2 = get_data_dataframe('2020-06-06', '2021-06-06', 'Ethereum')
out_df2.name = "Ethereum"

out_bt = custom_backtest(out_df1, out_df2, 200000)
print(get_equity_curve(out_bt))
print(len(get_equity_curve(out_bt)))"""
