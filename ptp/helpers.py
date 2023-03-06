import os
from dotenv import load_dotenv

from pymongo import MongoClient

import pandas as pd
import datetime

import numpy as np

from yahoofinancials import YahooFinancials

import requests
import json

import statsmodels.tsa.stattools as ts

load_dotenv()
DATABASE_ACCESS = os.getenv("DATABASE_ACCESS")
client = MongoClient(DATABASE_ACCESS)
db = client.pairs_trading


def clear_db():
    btc = db.btc
    eth = db.eth
    ltc = db.ltc
    bch = db.bch
    xrp = db.xrp

    coins = [btc, eth, ltc, bch, xrp]
    for i in range(len(coins)):
        coins[i].delete_many({})


def create_csv(symbol):
    yahoo_financials = YahooFinancials(symbol)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = yahoo_financials.get_historical_price_data("2016-06-01", today, "daily")
    df = pd.DataFrame(data[symbol]['prices'])
    # df = df.drop('date', axis=1).set_index('formatted_date')
    # df.index.names = ['date']
    df.rename(columns={"date": "unix", "formatted_date": "date"}, inplace=True)
    df.to_csv(fr'C:\Users\yboy2\PycharmProjects\pairs-trading-project\data\{symbol}_dailydata.csv',index=False)


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


def get_trades_df(bt):
    names, size, entry_price, exit_price, pnl, entry_time, exit_time, z_score, op = [], [], [], [], [], [], [], [], []
    index = []
    index_num = 1
    for i in bt.trades:
        index.extend([index_num, index_num])
        index_num += 1
        names.extend([i[0].coin, i[1].coin])
        size.extend([i[0].quantity, i[1].quantity])
        entry_price.extend([round(i[0].entry_price, 3), round(i[1].entry_price, 3)])
        exit_price.extend([round(i[0].exit_price, 3), round(i[1].exit_price, 3)])
        pnl.extend([round(i[0].pnl, 3), round(i[1].pnl, 3)])
        entry_time.extend([i[0].date.strftime('%Y-%m-%d'), i[1].date.strftime('%Y-%m-%d')])
#        exit_time.extend([i[0].close_date.strftime('%Y-%m-%d'), i[1].close_date.strftime('%Y-%m-%d')])
        z_score.extend([round(i[0].z_score, 3), round(i[1].z_score, 3)])
        op.extend([i[0].type, i[1].type])

    arr = np.array([index, names, op, entry_time, size, entry_price, exit_price, pnl, z_score], dtype=object)
    arr = arr.T
    df = pd.DataFrame(arr, columns=['Index', 'Name', 'Operation', 'Date',
                                    'Size', 'Entry Price', 'Exit Price', 'PnL', 'Z-Score'])
    return df


def get_equity_curve(bt):
    return bt.portfolio_values


def text_to_csv(text_file, collection_name):
    collection = db[collection_name]
    filecontent = []
    with open(text_file) as f:
        for line in f:
            date = text_file.at[line, 'date']
            d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
            high = text_file.at[line, 'high']
            low = text_file.at[line, 'low']
            open = text_file.at[line, 'open']
            close = text_file.at[line, 'close']
            volume = float(text_file.at[line, 'volume'])
            avg = (high + low) / 2
            element = {
                "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
            }
            filecontent.append(element)
    collection.insert_many(filecontent)


def import_coin(csv_file, collection_name):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    collection = db[collection_name]
    sheet = pd.read_csv(csv_file)
    data = []
    rows = len(sheet.index)
    for i in range(rows):
        date = sheet.at[i, 'date']
        try:
            d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
        except:
            d1 = datetime.datetime.strptime(date, "%m/%d/%Y")
        high = sheet.at[i, 'high']
        low = sheet.at[i, 'low']
        open = sheet.at[i, 'open']
        close = sheet.at[i, 'close']
        volume = float(sheet.at[i, 'volume'])
        avg = (high + low) / 2
        element = {
            "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
        }
        data.append(element)
    collection.insert_many(data)


def update_csv_db(symbol, lastdate):
    coins = create_symbols_coins_collections()[1]
    coin = coins[symbol]

    yahoo_financials = YahooFinancials(symbol)
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    lastdate = (lastdate + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    data = yahoo_financials.get_historical_price_data(lastdate, today, "daily")

    df = pd.DataFrame(data[symbol]['prices'])
    # df = df.drop('date', axis=1).set_index('formatted_date')
    # df.index.names = ['date']
    df.rename(columns={"date": "unix", "formatted_date": "date"}, inplace=True)
    sheet_name = 'data/%s_dailydata.csv' % symbol
    data_to_upload = []
    for index, row in df.iterrows():
        date = row['date']

        d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
        # print(d1)

        high = row['high']
        low = row['low']
        open = row['open']
        close = row['close']
        volume = float(row['volume'])
        avg = (high + low) / 2
        element = {
            "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
        }
        data_to_upload.append(element)
    coin.insert_many(data_to_upload)
    df.to_csv('data/%s_dailydata.csv' % symbol,mode='a', index=False, header=False)


def upload_csvs(sheet, coin):
    data = []
    rows = len(sheet.index)
    for i in range(rows):
        date = sheet.at[i, 'date']
        d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
        high = sheet.at[i, 'high']
        low = sheet.at[i, 'low']
        open = sheet.at[i, 'open']
        close = sheet.at[i, 'close']
        volume = float(sheet.at[i, 'volume'])
        avg = (high + low) / 2
        element = {
            "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
        }
        data.append(element)
    coin.insert_many(data)


def update_all():
    symbols = create_symbols_coins_collections()[0]
    coins = create_symbols_coins_collections()[1]
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    for symbol in symbols:
        if symbol not in ['BTC-USD', 'ETH-USD', 'BCH-USD', 'XRP-USD', 'LTC-USD']:
            continue
        coin = coins[symbol]
        last_date = coin.find().limit(1).sort([('$natural', -1)])[0]['Date'].date().strftime("%Y-%m-%d")
        if last_date != today:
            print(last_date, today)
            update_csv_db(symbol, datetime.datetime.strptime(last_date, "%Y-%m-%d"))
            print("updated symbol")


def create_symbols_coins_collections():
    collections = []
    symbols = []
    for i in db.list_collection_names():
        symbols.append(i.upper() + "-USD")
        collections.append(db[i])

    coins = {symbols[i]: collections[i] for i in range(len(symbols))}
    return symbols, coins


def update_db():
    symbols = create_symbols_coins_collections()[0]
    coins = create_symbols_coins_collections()[1]
    # we set which pair we want to retrieve data for
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    for symbol in symbols:
        if symbol not in ['BTC-USD', 'ETH-USD', 'BCH-USD', 'XRP-USD', 'LTC-USD']:
            continue
        file_name = 'data/%s_dailydata.csv' % symbol
        sheet = pd.read_csv(file_name)
        with open(file_name, "r") as f1:
            last_date = ""
            last_line = f1.readlines()[-1]
            for i in range(-11, -1, 1):
                last_date += last_line[i]
        if last_date != today:
            print(last_date, today)
            last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
            #update_csv_db(symbol, last_date)
            #print("updated %s" % file_name)

        upload_csvs(sheet, coins[symbol])
        print("uploaded %s" % symbol)


def find_best_pairs(date1, date2):
    coin_symbols = ["btc", "eth", "ltc", "xrp", "bch"]
    values_to_return = []
    for i in range(len(coin_symbols)-1):
        for j in range(i+1, len(coin_symbols)):
            prices1 = np.array(get_data(date1, date2, coin_symbols[i])[0])
            prices2 = np.array(get_data(date1, date2, coin_symbols[j])[0])
            # print("prices 1 %s %s" % (len(prices1), coin_symbols[i]))
            # print("prices 2 %s %s" % (len(prices2), coin_symbols[j]))
            values_to_return.append([coin_symbols[i], coin_symbols[j],
                                     find_correlation(prices1, prices2),
                                     find_cointegration(prices1, prices2)])
    df = pd.DataFrame(values_to_return, columns=['Coin1', 'Coin2', 'Correlation', 'Cointegration P-Value'])

    return df


def get_dates(start_date, end_date):
    start_date = datetime.datetime.fromisoformat(start_date)
    end_date = datetime.datetime.fromisoformat(end_date)
    day_count = (end_date - start_date).days + 1
    dates_array = []
    for single_date in (start_date + datetime.timedelta(n) for n in range(day_count)):
        dates_array.append(single_date)
    """d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    # d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    # d2 = '{d.month} {d.day} {d.year}'.format(d=d2)
    dates = coin.find({'Date': {"$gte":  d1, "$lte":  d2}})
    dates_array = []
    for i in dates:
        dates_array.append(i['Date'])"""
    return dates_array


def get_dates_string_daily(dates):
    string_dates = []
    for i in range(len(dates)):
        string_dates.append('{d.month}-{d.day}-{d.year}'.format(d=dates[i]))
    return string_dates


def get_data(date1, date2, coin_str):
    coins = create_collections_coins()
    coin = coins[coin_str]
    average_prices, opens, highs, lows, closes, volumes, open_interest = [], [], [], [], [], [], []

    # avg1, open1, high1, low1, close1, volume1
    # avg2, open2, high2, low2, close2, volume2

    d1 = datetime.datetime.fromisoformat(date1)
    # d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
    d2 = datetime.datetime.fromisoformat(date2)
    # d2 = '{d.month} {d.day} {d.year}'.format(d=d2)
    data_range = coin.find({'Date': {"$gte": d1, "$lte": d2}})
    for i in data_range:
        average_prices.append(i['Average'])
        opens.append(i['Open'])
        highs.append(i['High'])
        lows.append(i['Low'])
        closes.append(i['Close'])
        volumes.append(i['Volume'])
        open_interest.append(0)
    """average_prices.reverse()
    opens.reverse()
    highs.reverse()
    lows.reverse()
    closes.reverse()
    volumes.reverse()"""
    print(len(average_prices))
    return average_prices, opens, highs, lows, closes, volumes, open_interest


def get_data_dataframe(d1, d2, coin_str):
    # d1, d2 = date1/2
    # get dates
    dates = np.array(get_dates(d1, d2))
    # dates = np.flip(dates)

    # get values
    avg1, open1, high1, low1, close1, volume1, open_interest = np.array(get_data(d1, d2, coin_str))
    vals = np.array(get_data(d1, d2, coin_str))

    # make array
    # arr = np.array([dates, open1, high1, low1, close1, volume1, open_interest], dtype=object)
    arr = np.array(vals, dtype=object)
    arr = arr.T
    # make data frame
    df = pd.DataFrame(arr,  columns=['Average', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'], index=dates)
    # df.set_index('Date', inplace=True, drop=True)
    return df


"""
def auto_update_csv(coin_str):
    coins = create_collections_coins()
    coin = coins[coin_str]
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    last_date = coin.find().limit(1).sort([('$natural', -1)])[0]['Date'].date()
    first_date = coin.find()[0]['Date'].date()
    print(last_date)
    print(first_date)
    print(coin_str)
    if last_date.strftime('%Y-%m-%d') != yesterday and first_date.strftime("%Y-%m-%d") != yesterday:
        if coin_str in ['btc', 'eth', 'bch', 'xrp', 'ltc']:
            # print("updated %s date!" % coin_str)
            # coin_symbol = coin_str.upper() + "-USD"
            # update_csv_db(coin_symbol, last_date)
            update_all()
"""


def check_dates(coin_str1, coin_str2, start_date, end_date):
    coins = create_collections_coins()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    # auto_update_csv(coin_str1)
    # auto_update_csv(coin_str2)
    update_all()
    coin1 = coins[coin_str1]
    coin2 = coins[coin_str2]
    last_date1 = coin1.find().limit(1).sort([('$natural', -1)])[0]['Date'].date()
    last_date2 = coin2.find().limit(1).sort([('$natural', -1)])[0]['Date'].date()
    first_date1 = coin1.find()[0]['Date'].date()
    first_date2 = coin2.find()[0]['Date'].date()
    if last_date1 < end_date:
        end_date = last_date1
    if last_date2 < end_date:
        end_date = last_date2
    if first_date1 > start_date:
        start_date = first_date1
    if first_date2 > start_date:
        start_date = first_date2
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def create_collections_coins():
    collections = []
    for i in db.list_collection_names():
        collections.append(db[i])
    coins = {db.list_collection_names()[i]: collections[i] for i in range(len(db.list_collection_names()))}
    return coins



def fetch_daily_data(symbol):
    pair_split = symbol.split('/')  # symbol must be in format XXX/XXX ie. BTC/EUR
    symbol = pair_split[0] + '-' + pair_split[1]
    symbol_no_dash = pair_split[0] + pair_split[1]
    url = f'https://api.pro.coinbase.com/products/{symbol}/candles?granularity=86400'
    response = requests.get(url)
    if response.status_code == 200:  # check to make sure the response from server is good
        data = pd.DataFrame(json.loads(response.text), columns=['unix', 'low', 'high', 'open', 'close', 'volume'])
        data['date'] = pd.to_datetime(data['unix'], unit='s')  # convert to a readable date
        data['vol_fiat'] = data['volume'] * data['close']      # multiply the BTC volume by closing price to approximate fiat volume

        # if we failed to get any data, print an error...otherwise write the file
        if data is None:
            print("Did not return any data from Coinbase for this symbol")
        else:
            data.to_csv(fr'C:\Users\yboy2\PycharmProjects\pairs-trading-project\data\{symbol_no_dash}_dailydata.csv', index=False)
    else:
        print("Did not receieve OK response from Coinbase API")


def upload(sheet, name, coin):
    data = []
    rows = len(sheet.index)
    for i in range(rows):
        date = sheet.at[i, 'date']

        d1 = datetime.datetime.strptime(date, "%Y-%m-%d")

        high = sheet.at[i, 'high']
        low = sheet.at[i, 'low']
        open = sheet.at[i, 'open']
        close = sheet.at[i, 'close']
        volume = sheet.at[i, 'volume']
        avg = (high + low) / 2
        print(type(high), type(low), type(open), type(close), type(volume), type(avg))
        element = {
            "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
        }
        data.append(element)
        print(name, "inserted document: ", i)
    coin.insert_many(data)


def read_update():
    btc = db.btc
    eth = db.eth
    ltc = db.ltc
    bch = db.bch
    xrp = db.xrp

    coins = {
        "BTCUSD": btc,
        "ETHUSD": eth,
        "LTCUSD": ltc,
        "XRPUSD": xrp,
        "BCHUSD": bch
    }

    # we set which pair we want to retrieve data for
    data = ["BTC/USD", "ETH/USD", "LTC/USD", "XRP/USD", "BCH/USD"]
    for i in data:
        fetch_daily_data(symbol=i)
        coin_symbol = i.replace('/', '')
        file_name = 'data/%s_dailydata.csv' % coin_symbol
        sheet = pd.read_csv(file_name)
        upload(sheet, coin_symbol, coins[coin_symbol])


def get_values_pair(date1, date2, initial, df1, df2):
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    days = d2 - d1
    days = days.days
    years = days / 365

    final1 = df1["Equity Final [$]"]
    final2 = df2["Equity Final [$]"]

    final_equity = round(final1 + final2, 2)
    final = "{:,}".format(final_equity)

    trades = df1["# Trades"] + df2["# Trades"]
    cagr_result = round(((((final_equity / initial) ** (1/years)) - 1) * 100), 2)
    cagr = format_nums(cagr_result) + "%"

    roi_result = round((((final_equity - initial) / initial) * 100), 2)
    roi = format_nums(roi_result) + "%"

    total_pl = round((final1 + final2 - initial), 2)
    total_pl = format_nums(total_pl)

    initial = round(initial, 2)
    initial = "{:,}".format(initial)

    return {"cagr": cagr, "roi": roi, "total_pl": total_pl, "initial": initial, "final": final, "trades": trades}


def get_values(date1, date2, initial, df, equity_curve):
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    days = d2 - d1
    days = days.days
    years = days / 365

    final = equity_curve[-1]

    final_equity = round(final, 2)
    final = "{:,}".format(final_equity)

    trades = len(df)
    cagr_result = round(((((final_equity / initial) ** (1/years)) - 1) * 100), 2)
    cagr = format_nums(cagr_result) + "%"

    roi_result = round((((final_equity - initial) / initial) * 100), 2)
    roi = format_nums(roi_result) + "%"

    total_pl = round((final_equity - initial), 2)
    total_pl = format_nums(total_pl)

    initial = round(initial, 2)
    initial = "{:,}".format(initial)

    return {"cagr": cagr, "roi": roi, "total_pl": total_pl, "initial": initial, "final": final, "trades": trades}


def format_nums(num):
    if num > 0:
        return "+" + "{:,}".format(num)
    else:
        return "{:,}".format(num)


def find_correlation(price1, price2):
    return round(np.corrcoef(price1, price2)[1, 0], 5)


def find_cointegration(price1, price2):
    return round(ts.coint(price1, price2)[1], 5)
