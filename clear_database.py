from pymongo import MongoClient
import datetime

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test")

db = client.pairs_trading

btc = db.btc
eth = db.eth
ltc = db.ltc
bch = db.bch
xrp = db.xrp

coins = [btc, eth, ltc, bch, xrp]

for i in range(len(coins)):
    print(type(coins[i]))
    coins[i].delete_many({})

