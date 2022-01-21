import pandas as pd
from pymongo import MongoClient
import datetime

sheet = pd.read_csv('data/gemini_BTCUSD_day.csv')

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test")

db = client.pairs_trading

btc = db.btc

date = sheet.at[10, 'Date'].replace(" 4:00", "").replace("/", " ")

print(datetime.datetime.strptime(btc.find_one({"Date": date})["Date"], "%m %d %Y").date())