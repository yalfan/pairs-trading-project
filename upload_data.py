import pandas as pd
from pymongo import MongoClient
import numpy as np
import datetime
from yahoofinancials import YahooFinancials


client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)

db = client.pairs_trading


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


if __name__ == "__main__":
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
            # update_csv_db(symbol, last_date)
            # print("updated %s" % file_name)

        upload_csvs(sheet, coins[symbol])
        print("uploaded %s" % symbol)
