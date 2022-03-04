import pandas as pd
from pymongo import MongoClient
import numpy as np
import datetime

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)
db = client.pairs_trading

btc = db.btc
eth = db.eth
ltc = db.ltc
bch = db.bch
xrp = db.xrp

# d1 = "2021-10-10"
# d2 = "2021-12-6"


def get_dates(date1, date2, coin_string):
    coin = string_to_coin(coin_string)
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    # d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    # d2 = '{d.month} {d.day} {d.year}'.format(d=d2)
    dates = coin.find({'Date': {"$gte":  d1, "$lte":  d2}})
    dates_array = []
    for i in dates:
        dates_array.append(i['Date'])
    dates_array.reverse()
    return dates_array


def get_dates_string_daily(dates):
    string_dates = []
    for i in range(len(dates)):
        string_dates.append('{d.month}-{d.day}-{d.year}'.format(d=dates[i]))
    return string_dates


def get_data(date1, date2, coin_string):
    coin = string_to_coin(coin_string)
    average_prices, opens, highs, lows, closes, volumes = [], [], [], [], [], []

    # avg1, open1, high1, low1, close1, volume1
    # avg2, open2, high2, low2, close2, volume2

    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    # d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    # d2 = '{d.month} {d.day} {d.year}'.format(d=d2)
    data_range = coin.find({'Date': {"$gte": d1, "$lte": d2}})

    for i in data_range:
        average_prices.append(i['Average'])
        opens.append(i['Open'])
        highs.append(i['High'])
        lows.append(i['Low'])
        closes.append(i['Close'])
        volumes.append(i['Volume'])
    average_prices.reverse()
    opens.reverse()
    highs.reverse()
    lows.reverse()
    closes.reverse()
    volumes.reverse()
    return average_prices, opens, highs, lows, closes, volumes


def get_data_dataframe(d1, d2, coin_string):
    dates = np.array(get_dates(d1, d2, coin_string))
    # dates = np.flip(dates)
    avg1, open1, high1, low1, close1, volume1 = np.array(get_data(d1, d2, coin_string))
    arr = np.array([dates, open1, high1, low1, close1, volume1], dtype=object)
    arr = arr.T
    df = pd.DataFrame(arr,  columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df.set_index('Date', inplace=True, drop=True)
    return df


def string_to_coin(coin_string):
    coin = {
        "Bitcoin": btc,
        "Ethereum": eth,
        "Litecoin": ltc,
        "BitCash": bch,
        "XRP": xrp
    }[coin_string]
    return coin
