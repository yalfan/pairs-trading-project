from upload_data import *

import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_ACCESS = os.getenv("DATABASE_ACCESS")
client = MongoClient(DATABASE_ACCESS)
db = client.pairs_trading


def text_to_csv(text_file, collection_name):
    collection = db[collection_name]
    filecontent = []
    with open(text_file) as f:
        for line in f:
            date = sheet.at[line, 'date']
            d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
            high = sheet.at[line, 'high']
            low = sheet.at[line, 'low']
            open = sheet.at[line, 'open']
            close = sheet.at[line, 'close']
            volume = float(sheet.at[line, 'volume'])
            avg = (high + low) / 2
            element = {
                "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
            }
            filecontent.append(element)
    collection.insert_many(filecontent)


def import_coin(csv_file, collection_name):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    collection = db[collection_name]
    sheet = pd.read_csv(csv_file)
    data = []
    rows = len(sheet.index)
    for i in range(rows):
        date = sheet.at[i, 'date']
        try:
            d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
        except:
            d1 = datetime.datetime.strptime(date, "%m/%d/%Y")
        high = sheet.at[i, 'high']
        low = sheet.at[i, 'low']
        open = sheet.at[i, 'open']
        close = sheet.at[i, 'close']
        volume = float(sheet.at[i, 'volume'])
        avg = (high + low) / 2
        element = {
            "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
        }
        data.append(element)
    collection.insert_many(data)