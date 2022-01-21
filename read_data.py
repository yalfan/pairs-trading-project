import pandas as pd
import datetime
from pymongo import MongoClient

sheet = pd.read_csv('data/gemini_BTCUSD_day.csv')

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test")

db = client.pairs_trading

btc = db.btc

rows = len(sheet.index)
for i in range(rows):
    date = sheet.at[i, 'Date'].replace(" 4:00", "").replace("/", " ")
    high = sheet.at[i, 'High']
    low = sheet.at[i, 'Low']
    volume = sheet.at[i, 'Volume']
    avg = (high + low)/2

    data = {
        "Date": date, "High": high, "Low": low, "Average": avg, "Volume": volume
    }

    btc.insert_one(data)

