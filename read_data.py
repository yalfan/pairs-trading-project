import pandas as pd
from pymongo import MongoClient
import datetime

import requests
import json


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


if __name__ == "__main__":

    client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)

    db = client.pairs_trading

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


