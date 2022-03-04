import pandas as pd
from pymongo import MongoClient
import numpy as np
import datetime
import time
start_time = time.time()


def main():
    btc_sheet = np.genfromtxt('data/gemini_BTCUSD_day.csv', skip_header=1, delimiter=',', dtype='str')
    eth_sheet = np.genfromtxt('data/gemini_ETHUSD_day.csv', skip_header=1, delimiter=',', dtype='str')
    ltc_sheet = np.genfromtxt('data/gemini_LTCUSD_day.csv', skip_header=1, delimiter=',', dtype='str')
    bch_sheet = np.genfromtxt('data/Bitstamp_BCHUSD_d.csv', skip_header=1, delimiter=',', dtype='str')
    xrp_sheet = np.genfromtxt('data/Bitstamp_XRPUSD_d.csv', skip_header=1, delimiter=',', dtype='str')

    # bch, xrp, btc, eth, ltc

    client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)

    db = client.pairs_trading

    btc = db.btc
    eth = db.eth
    ltc = db.ltc
    bch = db.bch
    xrp = db.xrp

    coins = [btc, eth, ltc, bch, xrp]

    names = ["btc", "eth", "ltc", "bch", "xrp"]

    sheets = [btc_sheet, eth_sheet, ltc_sheet, bch_sheet, xrp_sheet]

    for j in range(len(sheets)):
        name = names[j]
        coin = coins[j]
        sheet = sheets[j]
        data = []
        for i in range(1, len(sheet[:, 1])):

            dates = sheet[:, 1]
            opens = sheet[:, 3]
            highs = sheet[:, 4]
            lows = sheet[:, 5]
            closes = sheet[:,6]
            volumes = sheet[:, 7]

            date = dates[i].replace(" 4:00", "").replace("/", " ").replace("-", " ") \
                .replace(" 00:00:00", "").replace(" 04:00:00", "")
            if name == "btc":
                date = datetime.datetime.strptime(date, "%m %d %Y")
            else:
                date = datetime.datetime.strptime(date, "%Y %m %d")

            high = float(highs[i])
            low = float(lows[i])
            volume = float(volumes[i])
            open = float(opens[i])
            close = float(closes[i])
            avg = (high + low) / 2

            element = {
                "Date": date, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
            }
            data.append(element)
            # print(name, "inserted document: ", i)
            # print("Date", date, "High", high, "Low", low, "Average", avg, "Volume", volume)
        coin.insert_many(data)


main()
print("--- %s seconds ---" % (time.time() - start_time))
