import pandas as pd
from pymongo import MongoClient
import datetime

sheet = pd.read_csv('data/gemini_BTCUSD_day.csv')

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test")

db = client.pairs_trading

btc = db.btc


rows = len(sheet.index)


def get_dates(date1, date2):
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d").date()
    d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d").date()
    d2 = '{d.month} {d.day} {d.year}'.format(d=d2)
    d1 = datetime.datetime.strptime(btc.find_one({"Date": d1})["Date"], "%m %d %Y").date()
    d2 = datetime.datetime.strptime(btc.find_one({"Date": d2})["Date"], "%m %d %Y").date()
    delta = abs((d2 - d1).days)
    dates = []
    for i in range(delta + 1):
        day = d1 + datetime.timedelta(i)
        dates.append(day)
    return dates


def get_data(dates):
    average_prices = []
    for i in range(len(dates)):
        date = '{d.month} {d.day} {d.year}'.format(d=dates[i])
        average_price = btc.find_one({"Date": date})["Average"]
        average_prices.append(average_price)
    return average_prices

