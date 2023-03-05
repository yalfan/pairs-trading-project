from pymongo import MongoClient

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_ACCESS = os.getenv("DATABASE_ACCESS")
client = MongoClient(DATABASE_ACCESS)
db = client.pairs_trading

btc = db.btc
eth = db.eth
ltc = db.ltc
bch = db.bch
xrp = db.xrp

coins = [btc, eth, ltc, bch, xrp]

for i in range(len(coins)):
    coins[i].delete_many({})
