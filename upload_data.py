import pandas as pd
from pymongo import MongoClient
import datetime
import time
start_time = time.time()


def main():
    btc_sheet = pd.read_csv('data/gemini_BTCUSD_day.csv', skiprows=1)
    eth_sheet = pd.read_csv('data/gemini_ETHUSD_day.csv', skiprows=1)
    ltc_sheet = pd.read_csv('data/gemini_LTCUSD_day.csv', skiprows=1)
    bch_sheet = pd.read_csv('data/Bitstamp_BCHUSD_d.csv', skiprows=1)
    xrp_sheet = pd.read_csv('data/Bitstamp_XRPUSD_d.csv', skiprows=1)

    # bch, xrp, btc, eth, ltc

    client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)

    db = client.pairs_trading

    btc = db.btc
    eth = db.eth
    ltc = db.ltc
    bch = db.bch
    xrp = db.xrp

    coins = [btc, eth, ltc, bch, xrp]

    # for debugging purposes
    names = ["btc", "eth", "ltc", "bch", "xrp"]

    sheets = [btc_sheet, eth_sheet, ltc_sheet, bch_sheet, xrp_sheet]
    for i in range(len(coins)):

        name = names[i]

        coin = coins[i]
        sheet = sheets[i]
        rows = len(sheets[i].index)
        data = []
        for i in range(rows):
            date = sheet.at[i, 'Date'].replace(" 4:00", "").replace("/", " ").replace("-", " ").replace(" 00:00:00",
                                                                                                        "").replace(
                " 04:00:00", "")

            if name == "btc":
                d1 = datetime.datetime.strptime(date, "%m %d %Y")
            else:
                d1 = datetime.datetime.strptime(date, "%Y %m %d")
            # .replace(" 4:00", "").replace("/", " ").replace("-", " ").replace(" 00:00:00", "").replace(" 04:00:00", "")
            high = sheet.at[i, 'High']
            low = sheet.at[i, 'Low']
            open = sheet.at[i, 'Open']
            close = sheet.at[i, 'Close']
            volume = sheet.at[i, 'Volume']
            avg = (high + low) / 2

            element = {
                "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
            }
            data.append(element)
            print(name, "inserted document: ", i)
        coin.insert_many(data)

main()
print("--- %s seconds ---" % (time.time() - start_time))
