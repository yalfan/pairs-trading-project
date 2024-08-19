import pandas as pd
import datetime


def SMA(arr: pd.Series, n: int):
    return pd.Series(arr).rolling(n).mean()


def STD_DEV(arr: pd.Series, n: int):
    return pd.Series(arr).rolling(n).std()


def RATIO(arr: pd.Series):
    return pd.Series(arr)


def Z_SCORE(arr: pd.Series):
    return pd.Series(arr)


class PairRatio:
    def __init__(self, ratio, sma, std_dev, z_score, df1, df2, params):
        ma_period, std_period, max_dur, entry_threshold, exit_threshold, sl_threshold = \
            params[0], params[1], params[2], params[3], params[4], params[5]

        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.max_dur = max_dur
        self.ma_period = ma_period
        self.std_period = std_period
        self.sl_threshold = sl_threshold
        self.purchase_price1 = 0
        self.purchase_price2 = 0
        self.days_held = 0
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
        self.equity = params[6]
        self.i = 0
        self.portfolio = 0
        self.portfolio_values = []
        self.today = datetime.datetime.today().date()
        # less or more
        self.lom = {
            self.coin1: "Less" if self.prices1[0] < self.prices2[0] else "More",
            self.coin2: "Less" if self.prices2[0] < self.prices1[0] else "More"
        }
        self.coins = {
            self.coin1: self.df1,
            self.coin2: self.df2
        }
        if self.max_dur == 0:
            self.max_dur = len(self.dates)

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
                if action == "Close" or self.stop_loss_action() or self.days_held >= self.max_dur:
                    self.close()
                else:
                    self.days_held += 1
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
        self.purchase_price1 = prices1[self.i]
        self.purchase_price2 = prices2[self.i]
        # date, price, quantity, type, coin, z_score
        position1 = Position(self.dates[self.i], prices1[self.i], x, "Short", coin1,
                             self.z_scores[self.i])  # Short coin1
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
        self.purchase_price1 = prices1[self.i]
        self.purchase_price2 = prices2[self.i]
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
        self.days_held = 0
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
        # ClosePosition(date, entry_price, exit_price, quantity, type, coin, z_score)
        # p1, p2 = current positions
        # close1, close2 = close actions
        p1 = self.trades[-1][0]
        close1 = ClosePosition(self.dates[self.i], p1.entry_price,
                               self.coins.get(p1.coin)['Close'][self.i],
                               p1.quantity, p1.type, p1.coin, self.z_scores[self.i])
        close1.set_pnl_operation()

        p2 = self.trades[-1][1]
        close2 = ClosePosition(self.dates[self.i], p2.entry_price,
                               self.coins.get(p2.coin)['Close'][self.i],
                               p2.quantity, p2.type, p2.coin, self.z_scores[self.i])
        close2.set_pnl_operation()

        self.trades.append([close1, close2])
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
        portfolio_value = self.equity + self.portfolio - coin.quantity * coin.entry_price
        self.portfolio_values.append(portfolio_value)

    def update_short(self, coin):
        self.portfolio = coin.quantity * self.coins.get(coin.coin)['Close'][self.i]
        portfolio_value = self.equity - self.portfolio + coin.quantity * coin.entry_price
        self.portfolio_values.append(portfolio_value)

    def update_portfolio_values(self, c1, c2):
        # curr = current value
        curr1 = c1.quantity * self.coins.get(c1.coin)['Close'][self.i]
        curr2 = c2.quantity * self.coins.get(c2.coin)['Close'][self.i]
        # iv = initial value
        iv1 = c1.quantity * c1.entry_price
        iv2 = c2.quantity * c2.entry_price
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

    def stop_loss_action(self):
        # if default stop/loss, don't use stop loss
        if self.sl_threshold == 0:
            return False
        c1, c2 = self.position[0], self.position[1]
        curr1 = c1.quantity * self.coins.get(c1.coin)['Close'][self.i]
        curr2 = c2.quantity * self.coins.get(c2.coin)['Close'][self.i]

        if curr1 < c1.quantity * self.purchase_price1 * (1 - self.sl_threshold) or \
                curr1 > c1.quantity * self.purchase_price1 * (1 + self.sl_threshold) or \
                curr2 < c2.quantity * self.purchase_price2 * (1 - self.sl_threshold) or \
                curr2 > c2.quantity * self.purchase_price2 * (1 + self.sl_threshold):

            print(curr1, self.purchase_price1 * (1 - self.sl_threshold), self.purchase_price1 * (1 + self.sl_threshold))
            print(curr2, self.purchase_price2 * (1 - self.sl_threshold), self.purchase_price2 * (1 + self.sl_threshold))
            return True


class Position:
    def __init__(self, date, price, quantity, type, coin, z_score):
        self.date = date
        self.entry_price = price
        self.quantity = quantity
        self.type = type
        self.coin = coin
        self.pnl = 0
        self.z_score = z_score
        self.exit_price = 0


class ClosePosition:
    def __init__(self, date, entry_price, exit_price, quantity, type, coin, z_score):
        self.entry_price = entry_price
        self.quantity = quantity
        self.type = type
        self.coin = coin
        self.date = date
        self.z_score = z_score
        self.exit_price = exit_price
        # gets profit and loss than
        self.pnl = 0

    def set_pnl_operation(self):
        if self.type == "Long":
            self.pnl = self.quantity * self.exit_price - self.quantity * self.entry_price
            self.type = "Close"
        elif self.type == "Short":
            self.pnl = self.quantity * self.entry_price - self.quantity * self.exit_price
            self.type = "Close"


def custom_backtest(df1, df2, params):
    ma_period, std_period, max_dur, entry_threshold, exit_threshold, sl_threshold = \
        params[0], params[1], params[2], params[3], params[4], params[5]
    ratio = (df1['Close'] / df2['Close']).rename("Ratio")
    sma = SMA(ratio, ma_period).rename("SMA")
    std_dev = STD_DEV(ratio, std_period).rename("STD")
    z_score = pd.Series((ratio - sma) / std_dev).rename("Z_SCORE")
    bt = PairRatio(ratio, sma, std_dev, z_score, df1, df2, params)
    bt.run()
    return bt
