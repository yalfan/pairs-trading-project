import pandas
import pandas as pd
import numpy as np
import datetime
import json
from pymongo import MongoClient
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

from backtesting.test import SMA, GOOG

from values import *
from query_data import *

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)

db = client.pairs_trading

btc = db.btc
eth = db.eth
ltc = db.ltc
bch = db.bch
xrp = db.xrp

d1 = "2016-12-6"
d2 = "2021-6-6"

coin_string = "Bitcoin"

date1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
date2 = datetime.datetime.strptime(d2, "%Y-%m-%d")

stuff = db.btc.find({'Date': {"$gte":  date1, "$lte":  date2}})


df = get_data_dataframe(d1, d2, "Bitcoin")

cagr1, roi1 = get_values(d1, d2, 100000, 31673.2)
values = get_values(d1, d2, 100000, 31673.2)
json_values = json.dumps(values)

print(type(json_values))
