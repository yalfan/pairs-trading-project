import pandas as pd
import numpy as np
import datetime
from upload_data import *

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)
db = client.pairs_trading
print(type(db.bch))
coin = db.list_collection_names()[0]
print(type(db.coin))
print(coin)
