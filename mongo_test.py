from pymongo import MongoClient

client = MongoClient(port=27017)

db = client.pairs_trading

btc = db.btc

data = {
    "Date": 1/9/2022, "High":42782.58, "Low":41214.24, "Volume":688.35
}

db.btc.insert_one(data)