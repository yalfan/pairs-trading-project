import pandas as pd
from pymongo import MongoClient
import numpy as np
import datetime


def upload(sheet, coin):
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
        print("inserted document")
    coin.insert_many(data)


def edit_csv(symbol):
    file_name = 'data/new_%s_dailydata.csv' % symbol
    df = pd.read_csv(file_name)
    df['date'] = df['date'].apply(replace_hours)
    # unix,low,high,open,close,volume,date,vol_fiat
    df = df[['unix', 'low', 'high', 'open', 'close', 'volume', 'date', 'vol_fiat']]
    columns = ['low', 'high', 'open', 'close', 'volume']
    for i in columns:
        df[i] = df[i].apply(round_numbers)
    df.to_csv(fr'C:\Users\yboy2\PycharmProjects\pairs-trading-project\data\temp.csv', index=False)


def replace_hours(x):
    return x.replace(" 00:00:00", "")


def round_numbers(x):
    if x in ['low', 'high', 'open', 'close', 'volume']:
        return x
    return round(float(x), 5)


if __name__ == "__main__":
    client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)

    db = client.pairs_trading

    btc = db.btc
    eth = db.eth
    ltc = db.ltc
    bch = db.bch
    xrp = db.xrp

    coins = {
        "BTC-USD": btc,
        "ETH-USD": eth,
        "LTC-USD": ltc,
        "XRP-USD": xrp,
        "BCH-USD": bch
    }
    # we set which pair we want to retrieve data for
    symbols = ["BTC-USD", "ETH-USD", "LTC-USD", "XRP-USD", "BCH-USD"]
    for i in symbols:
        file_name = 'data/%s_dailydata.csv' % i
        sheet = pd.read_csv(file_name)
        upload(sheet, coins[i])

