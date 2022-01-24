import pandas as pd
from pymongo import MongoClient

btc_sheet = pd.read_csv('data/gemini_BTCUSD_day.csv')

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test")

db = client.pairs_trading

btc = db.btc
eth = db.eth
ltc = db.ltc
zec = db.zec

btc_rows = len(btc_sheet.index)
for i in range(btc_rows):
    date = btc_sheet.at[i, 'Date'].replace(" 4:00", "").replace("/", " ")
    high = btc_sheet.at[i, 'High']
    low = btc_sheet.at[i, 'Low']
    volume = btc_sheet.at[i, 'Volume']
    avg = (high + low)/2

    data = {
        "Date": date, "High": high, "Low": low, "Average": avg, "Volume": volume
    }

    btc.insert_one(data)

