import pandas as pd
from pymongo import MongoClient
import numpy as np
import datetime
import time
import csv

import requests
import json

import yfinance as yf
from yahoofinancials import YahooFinancials


def create_csv(symbol):
    yahoo_financials = YahooFinancials(symbol)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = yahoo_financials.get_historical_price_data("2016-06-01", today, "daily")
    df = pd.DataFrame(data[symbol]['prices'])
    # df = df.drop('date', axis=1).set_index('formatted_date')
    # df.index.names = ['date']
    df.rename(columns={"date": "unix", "formatted_date": "date"}, inplace=True)
    df.to_csv(fr'C:\Users\yboy2\PycharmProjects\pairs-trading-project\data\{symbol}_dailydata.csv',index=False)


if __name__ == "__main__":
    # we set which pair we want to retrieve data for
    symbols = ["BTC-USD", "ETH-USD", "LTC-USD", "XRP-USD", "BCH-USD"]
    for i in symbols:
        create_csv(i)

