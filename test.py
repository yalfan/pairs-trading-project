import pandas as pd
from pymongo import MongoClient

btc_sheet = pd.read_csv('data/gemini_BTCUSD_day.csv', skiprows=1)
eth_sheet = pd.read_csv('data/gemini_ETHUSD_day.csv', skiprows=1)
ltc_sheet = pd.read_csv('data/gemini_LTCUSD_day.csv', skiprows=1)
bch_sheet = pd.read_csv('data/Bitstamp_BCHUSD_d.csv', skiprows=1)
xrp_sheet = pd.read_csv('data/Bitstamp_XRPUSD_d.csv', skiprows=1)

# bch, xrp, btc, eth, ltc

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test")

db = client.pairs_trading

eth = db.eth

sheet = eth_sheet
rows = len(sheet.index)
for i in range(rows):
    date = sheet.at[i, 'Date'].replace(" 4:00", "").replace("/", " ").replace("-", " ").replace(" 00:00:00", "").replace(" 04:00:00", "")
    high = sheet.at[i, 'High']
    low = sheet.at[i, 'Low']
    volume = sheet.at[i, 'Volume']
    avg = (high + low)/2

    data = {
        "Date": date, "High": high, "Low": low, "Average": avg, "Volume": volume
    }

    eth.insert_one(data)
    print("inserted document: ", i)
