import pandas as pd
from pymongo import MongoClient
import datetime

btc_sheet = pd.read_csv('data/gemini_BTCUSD_day.csv', skiprows=1)
eth_sheet = pd.read_csv('data/gemini_ETHUSD_day.csv', skiprows=1)
ltc_sheet = pd.read_csv('data/gemini_LTCUSD_day.csv', skiprows=1)
bch_sheet = pd.read_csv('data/Bitstamp_BCHUSD_d.csv', skiprows=1)
xrp_sheet = pd.read_csv('data/Bitstamp_XRPUSD_d.csv', skiprows=1)

# bch, xrp, btc, eth, ltc

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test")

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
    for i in range(rows):
        date = sheet.at[i, 'Date'].replace(" 4:00", "").replace("/", " ").replace("-", " ").replace(" 00:00:00", "").replace(" 04:00:00", "")
        if name == "btc":
            d1 = datetime.datetime.strptime(date, "%m %d %Y").date()
            d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
        else:
            d1 = datetime.datetime.strptime(date, "%Y %m %d").date()
            d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
        # .replace(" 4:00", "").replace("/", " ").replace("-", " ").replace(" 00:00:00", "").replace(" 04:00:00", "")
        high = sheet.at[i, 'High']
        low = sheet.at[i, 'Low']
        volume = sheet.at[i, 'Volume']
        avg = (high + low)/2

        data = {
            "Date": d1, "High": high, "Low": low, "Average": avg, "Volume": volume
        }

        coin.insert_one(data)
        print(name, "inserted document: ", i)
