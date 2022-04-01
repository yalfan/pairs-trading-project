import pandas as pd
from pymongo import MongoClient
import numpy as np
import datetime

from yahoofinancials import YahooFinancials


client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)
db = client.pairs_trading

btc = db.btc
eth = db.eth
ltc = db.ltc
bch = db.bch
xrp = db.xrp


def update_csv_db(symbol, lastdate, coin):
    yahoo_financials = YahooFinancials(symbol)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    lastdate = (lastdate + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    data = yahoo_financials.get_historical_price_data(lastdate, today, "daily")
    df = pd.DataFrame(data[symbol]['prices'])
    # df = df.drop('date', axis=1).set_index('formatted_date')
    # df.index.names = ['date']
    df.rename(columns={"date": "unix", "formatted_date": "date"}, inplace=True)
    data_to_upload = []
    for index, row in df.iterrows():
        date = row['date']

        d1 = datetime.datetime.strptime(date, "%Y-%m-%d")

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
    df.to_csv(fr'C:\Users\yboy2\PycharmProjects\pairs-trading-project\data\{symbol}_dailydata.csv',mode='a', index=False, header=False)


if __name__ == "__main__":

    coins = {
        "BTC-USD": btc,
        "ETH-USD": eth,
        "LTC-USD": ltc,
        "XRP-USD": xrp,
        "BCH-USD": bch
    }
    # we set which pair we want to retrieve data for
    symbols = ["BTC-USD", "ETH-USD", "LTC-USD", "XRP-USD", "BCH-USD"]
    """for i in symbols:
        create_csv(i)"""

