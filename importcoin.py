import pandas as pd
from pymongo import MongoClient
from upload_data import *

client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)
db = client.pairs_trading

btc = db.btc
eth = db.eth
ltc = db.ltc
bch = db.bch
xrp = db.xrp

def importCoin(csv_path, db_name, coll_name, db_url='localhost', db_port=27000):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    client = MongoClient(db_url, db_port)
    db = client[db_name]
    coll = db[coll_name]
    data = pd.read_csv(csv_path)
    payload = json.loads(data.to_json(orient='records'))
    coll.remove()
    coll.insert(payload)
    return coll.count()