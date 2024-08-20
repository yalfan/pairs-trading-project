import os
from dotenv import load_dotenv

from pymongo import MongoClient

import pandas as pd
import datetime

import numpy as np

from yahoofinancials import YahooFinancials

import requests
import json

import statsmodels.tsa.stattools as ts

load_dotenv()
DATABASE_ACCESS = os.getenv("DATABASE_ACCESS")
client = MongoClient(DATABASE_ACCESS)
db = client.pairs_trading


def clear_db():
    btc = db.btc
    eth = db.eth
    ltc = db.ltc
    bch = db.bch
    xrp = db.xrp

    coins = [btc, eth, ltc, bch, xrp]
    for i in range(len(coins)):
        coins[i].delete_many({})


def create_csv(symbol):
    yahoo_financials = YahooFinancials(symbol)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = yahoo_financials.get_historical_price_data("2016-06-01", today, "daily")
    df = pd.DataFrame(data[symbol]['prices'])
    # df = df.drop('date', axis=1).set_index('formatted_date')
    # df.index.names = ['date']
    df.rename(columns={"date": "unix", "formatted_date": "date"}, inplace=True)
    df.to_csv(fr'C:\Users\yboy2\PycharmProjects\pairs-trading-project\data\{symbol}_dailydata.csv',index=False)


def get_trades_df(bt):
    names, size, entry_price, exit_price, pnl, entry_time, exit_time, z_score, op = [], [], [], [], [], [], [], [], []
    index = []
    index_num = 1
    for i in bt.trades:
        index.extend([index_num, index_num])
        index_num += 1
        names.extend([i[0].coin, i[1].coin])
        size.extend([i[0].quantity, i[1].quantity])
        entry_price.extend([round(i[0].entry_price, 3), round(i[1].entry_price, 3)])
        exit_price.extend([round(i[0].exit_price, 3), round(i[1].exit_price, 3)])
        pnl.extend([round(i[0].pnl, 3), round(i[1].pnl, 3)])
        entry_time.extend([i[0].date.strftime('%Y-%m-%d'), i[1].date.strftime('%Y-%m-%d')])
#        exit_time.extend([i[0].close_date.strftime('%Y-%m-%d'), i[1].close_date.strftime('%Y-%m-%d')])
        z_score.extend([round(i[0].z_score, 3), round(i[1].z_score, 3)])
        op.extend([i[0].type, i[1].type])

    arr = np.array([index, names, op, entry_time, size, entry_price, exit_price, pnl, z_score], dtype=object)
    arr = arr.T
    df = pd.DataFrame(arr, columns=['Index', 'Name', 'Operation', 'Date',
                                    'Size', 'Entry Price', 'Exit Price', 'PnL', 'Z-Score'])
    return df


def get_equity_curve(bt):
    return bt.portfolio_values


def text_to_csv(text_file, collection_name):
    collection = db[collection_name]
    filecontent = []
    with open(text_file) as f:
        for line in f:
            date = text_file.at[line, 'date']
            d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
            high = text_file.at[line, 'high']
            low = text_file.at[line, 'low']
            open = text_file.at[line, 'open']
            close = text_file.at[line, 'close']
            volume = float(text_file.at[line, 'volume'])
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


def upload_csvs(sheet, coin):
    data = []
    rows = len(sheet.index)
    for i in range(rows):
        date = sheet.at[i, 'date']
        d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
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
    coin.insert_many(data)


def update_all():
    symbols = create_symbols_coins_collections()[0]
    coins = create_symbols_coins_collections()[1]
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    for symbol in symbols:
        if symbol not in ['BTC-USD', 'ETH-USD', 'BCH-USD', 'XRP-USD', 'LTC-USD']:
            continue
        coin = coins[symbol]
        last_date = coin.find().limit(1).sort([('$natural', -1)])[0]['Date'].date().strftime("%Y-%m-%d")
        if last_date != today:
            print(last_date, today)
            update_csv_db(symbol, datetime.datetime.strptime(last_date, "%Y-%m-%d"))
            print("updated symbol")
    clean_csvs()


def create_symbols_coins_collections():
    collections = []
    symbols = []
    for i in db.list_collection_names():
        symbols.append(i.upper() + "-USD")
        collections.append(db[i])

    coins = {symbols[i]: collections[i] for i in range(len(symbols))}
    return symbols, coins


def update_csv_db(symbol, lastdate):
    coins = create_symbols_coins_collections()[1]
    coin = coins[symbol]

    yahoo_financials = YahooFinancials(symbol)
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    lastdate = (lastdate + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

    data = yahoo_financials.get_historical_price_data(lastdate, today, "daily")

    df = pd.DataFrame(data[symbol]['prices'])
    # df = df.drop('date', axis=1).set_index('formatted_date')
    # df.index.names = ['date']
    df.rename(columns={"date": "unix", "formatted_date": "date"}, inplace=True)
    sheet_name = 'ptp/data/%s_dailydata.csv' % symbol
    data_to_upload = []
    for index, row in df.iterrows():
        date = row['date']

        d1 = datetime.datetime.strptime(date, "%Y-%m-%d")
        # print(d1)

        high = row['high']
        low = row['low']
        open = row['open']
        close = row['close']
        volume = float(row['volume'])
        avg = (high + low) / 2
        element = {
            "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
        }
        data_to_upload.append(element)
    coin.insert_many(data_to_upload)
    df.to_csv(sheet_name, mode='a', index=False, header=False)


def update_db():
    symbols = create_symbols_coins_collections()[0]
    coins = create_symbols_coins_collections()[1]
    # we set which pair we want to retrieve data for
    today = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    for symbol in symbols:
        if symbol not in ['BTC-USD', 'ETH-USD', 'BCH-USD', 'XRP-USD', 'LTC-USD']:
            continue
        file_name = 'ptp/data/%s_dailydata.csv' % symbol
        sheet = pd.read_csv(file_name)
        with open(file_name, "r") as f1:
            last_date = ""
            last_line = f1.readlines()[-1]
            for i in range(-11, -1, 1):
                last_date += last_line[i]
        if last_date != today:
            print(last_date, today)
            last_date = datetime.datetime.strptime(last_date, "%Y-%m-%d")
            update_csv_db(symbol, last_date)
            print("updated %s" % file_name)

        clean_csvs()

        upload_csvs(sheet, coins[symbol])
        print("uploaded %s" % symbol)


def clean_csvs():
    symbols = create_symbols_coins_collections()[0]

    for symbol in symbols:
        file_name = 'ptp/data/%s_dailydata.csv' % symbol
        sheet = pd.read_csv(file_name)

        sheet.drop_duplicates(subset=None, inplace=True)

        # Write the results to a different file
        sheet.to_csv(file_name, index=False)


def find_best_pairs(date1, date2):
    coin_symbols = ["btc", "eth", "ltc", "xrp", "bch"]
    values_to_return = []
    for i in range(len(coin_symbols)-1):
        for j in range(i+1, len(coin_symbols)):
            prices1 = np.array(get_data(date1, date2, coin_symbols[i])[0])
            prices2 = np.array(get_data(date1, date2, coin_symbols[j])[0])
            # print("prices 1 %s %s" % (len(prices1), coin_symbols[i]))
            # print("prices 2 %s %s" % (len(prices2), coin_symbols[j]))
            values_to_return.append([coin_symbols[i], coin_symbols[j],
                                     find_correlation(prices1, prices2),
                                     find_cointegration(prices1, prices2)])
    df = pd.DataFrame(values_to_return, columns=['Coin1', 'Coin2', 'Correlation', 'Cointegration P-Value'])

    return df


def get_dates(start_date, end_date):
    start_date = datetime.datetime.fromisoformat(start_date)
    end_date = datetime.datetime.fromisoformat(end_date)
    day_count = (end_date - start_date).days + 1
    dates_array = []
    for single_date in (start_date + datetime.timedelta(n) for n in range(day_count)):
        dates_array.append(single_date)
    """d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    # d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    # d2 = '{d.month} {d.day} {d.year}'.format(d=d2)
    dates = coin.find({'Date': {"$gte":  d1, "$lte":  d2}})
    dates_array = []
    for i in dates:
        dates_array.append(i['Date'])"""
    return dates_array


def get_dates_string_daily(dates):
    string_dates = []
    for i in range(len(dates)):
        string_dates.append('{d.month}-{d.day}-{d.year}'.format(d=dates[i]))
    return string_dates


def get_data(date1, date2, coin_str):
    coins = create_collections_coins()
    coin = coins[coin_str]
    average_prices, opens, highs, lows, closes, volumes, open_interest = [], [], [], [], [], [], []

    # avg1, open1, high1, low1, close1, volume1
    # avg2, open2, high2, low2, close2, volume2

    d1 = datetime.datetime.fromisoformat(date1)
    # d1 = '{d.month} {d.day} {d.year}'.format(d=d1)
    d2 = datetime.datetime.fromisoformat(date2)
    # d2 = '{d.month} {d.day} {d.year}'.format(d=d2)
    data_range = coin.find({'Date': {"$gte": d1, "$lte": d2}})
    for i in data_range:
        average_prices.append(i['Average'])
        opens.append(i['Open'])
        highs.append(i['High'])
        lows.append(i['Low'])
        closes.append(i['Close'])
        volumes.append(i['Volume'])
        open_interest.append(0)
    """average_prices.reverse()
    opens.reverse()
    highs.reverse()
    lows.reverse()
    closes.reverse()
    volumes.reverse()"""
    print(len(average_prices))
    return average_prices, opens, highs, lows, closes, volumes, open_interest


def get_data_dataframe(d1, d2, coin_str):
    # d1, d2 = date1/2
    # get dates
    dates = np.array(get_dates(d1, d2))
    # dates = np.flip(dates)

    # get values
    avg1, open1, high1, low1, close1, volume1, open_interest = np.array(get_data(d1, d2, coin_str))
    vals = np.array(get_data(d1, d2, coin_str))

    # make array
    # arr = np.array([dates, open1, high1, low1, close1, volume1, open_interest], dtype=object)
    arr = np.array(vals, dtype=object)
    arr = arr.T
    # make data frame
    df = pd.DataFrame(arr,  columns=['Average', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest'], index=dates)
    # df.set_index('Date', inplace=True, drop=True)
    return df


"""
def auto_update_csv(coin_str):
    coins = create_collections_coins()
    coin = coins[coin_str]
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    last_date = coin.find().limit(1).sort([('$natural', -1)])[0]['Date'].date()
    first_date = coin.find()[0]['Date'].date()
    print(last_date)
    print(first_date)
    print(coin_str)
    if last_date.strftime('%Y-%m-%d') != yesterday and first_date.strftime("%Y-%m-%d") != yesterday:
        if coin_str in ['btc', 'eth', 'bch', 'xrp', 'ltc']:
            # print("updated %s date!" % coin_str)
            # coin_symbol = coin_str.upper() + "-USD"
            # update_csv_db(coin_symbol, last_date)
            update_all()
"""


def check_dates(coin_str1, coin_str2, start_date, end_date):
    coins = create_collections_coins()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    # auto_update_csv(coin_str1)
    # auto_update_csv(coin_str2)
    # update_all()
    coin1 = coins[coin_str1]
    coin2 = coins[coin_str2]
    last_date1 = coin1.find().limit(1).sort([('$natural', -1)])[0]['Date'].date()
    last_date2 = coin2.find().limit(1).sort([('$natural', -1)])[0]['Date'].date()
    first_date1 = coin1.find()[0]['Date'].date()
    first_date2 = coin2.find()[0]['Date'].date()
    if last_date1 < end_date:
        end_date = last_date1
    if last_date2 < end_date:
        end_date = last_date2
    if first_date1 > start_date:
        start_date = first_date1
    if first_date2 > start_date:
        start_date = first_date2
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def create_collections_coins():
    collections = []
    for i in db.list_collection_names():
        collections.append(db[i])
    coins = {db.list_collection_names()[i]: collections[i] for i in range(len(db.list_collection_names()))}
    return coins



def fetch_daily_data(symbol):
    pair_split = symbol.split('/')  # symbol must be in format XXX/XXX ie. BTC/EUR
    symbol = pair_split[0] + '-' + pair_split[1]
    symbol_no_dash = pair_split[0] + pair_split[1]
    url = f'https://api.pro.coinbase.com/products/{symbol}/candles?granularity=86400'
    response = requests.get(url)
    if response.status_code == 200:  # check to make sure the response from server is good
        data = pd.DataFrame(json.loads(response.text), columns=['unix', 'low', 'high', 'open', 'close', 'volume'])
        data['date'] = pd.to_datetime(data['unix'], unit='s')  # convert to a readable date
        data['vol_fiat'] = data['volume'] * data['close']      # multiply the BTC volume by closing price to approximate fiat volume

        # if we failed to get any data, print an error...otherwise write the file
        if data is None:
            print("Did not return any data from Coinbase for this symbol")
        else:
            data.to_csv(fr'C:\Users\yboy2\PycharmProjects\pairs-trading-project\data\{symbol_no_dash}_dailydata.csv', index=False)
    else:
        print("Did not receieve OK response from Coinbase API")


def upload(sheet, name, coin):
    data = []
    rows = len(sheet.index)
    for i in range(rows):
        date = sheet.at[i, 'date']

        d1 = datetime.datetime.strptime(date, "%Y-%m-%d")

        high = sheet.at[i, 'high']
        low = sheet.at[i, 'low']
        open = sheet.at[i, 'open']
        close = sheet.at[i, 'close']
        volume = sheet.at[i, 'volume']
        avg = (high + low) / 2
        print(type(high), type(low), type(open), type(close), type(volume), type(avg))
        element = {
            "Date": d1, "Open": open, "High": high, "Low": low, "Close": close, "Average": avg, "Volume": volume
        }
        data.append(element)
        print(name, "inserted document: ", i)
    coin.insert_many(data)


def read_update():
    btc = db.btc
    eth = db.eth
    ltc = db.ltc
    bch = db.bch
    xrp = db.xrp

    coins = {
        "BTCUSD": btc,
        "ETHUSD": eth,
        "LTCUSD": ltc,
        "XRPUSD": xrp,
        "BCHUSD": bch
    }

    # we set which pair we want to retrieve data for
    data = ["BTC/USD", "ETH/USD", "LTC/USD", "XRP/USD", "BCH/USD"]
    for i in data:
        fetch_daily_data(symbol=i)
        coin_symbol = i.replace('/', '')
        file_name = 'ptp/data/%s_dailydata.csv' % coin_symbol
        sheet = pd.read_csv(file_name)
        upload(sheet, coin_symbol, coins[coin_symbol])


def get_values_pair(date1, date2, initial, df1, df2):
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    days = d2 - d1
    days = days.days
    years = days / 365

    final1 = df1["Equity Final [$]"]
    final2 = df2["Equity Final [$]"]

    final_equity = round(final1 + final2, 2)
    final = "{:,}".format(final_equity)

    trades = df1["# Trades"] + df2["# Trades"]
    cagr_result = round(((((final_equity / initial) ** (1/years)) - 1) * 100), 2)
    cagr = format_nums(cagr_result) + "%"

    roi_result = round((((final_equity - initial) / initial) * 100), 2)
    roi = format_nums(roi_result) + "%"

    total_pl = round((final1 + final2 - initial), 2)
    total_pl = format_nums(total_pl)

    initial = round(initial, 2)
    initial = "{:,}".format(initial)

    return {"cagr": cagr, "roi": roi, "total_pl": total_pl, "initial": initial, "final": final, "trades": trades}


def get_values(date1, date2, initial, df, equity_curve):
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    days = d2 - d1
    days = days.days
    years = days / 365

    final = equity_curve[-1]

    final_equity = round(final, 2)
    final = "{:,}".format(final_equity)

    trades = len(df)
    cagr_result = round(((((final_equity / initial) ** (1/years)) - 1) * 100), 2)
    cagr = format_nums(cagr_result) + "%"

    roi_result = round((((final_equity - initial) / initial) * 100), 2)
    roi = format_nums(roi_result) + "%"

    total_pl = round((final_equity - initial), 2)
    total_pl = format_nums(total_pl)

    initial = round(initial, 2)
    initial = "{:,}".format(initial)

    return {"cagr": cagr, "roi": roi, "total_pl": total_pl, "initial": initial, "final": final, "trades": trades}


def format_nums(num):
    if num > 0:
        return "+" + "{:,}".format(num)
    else:
        return "{:,}".format(num)


def find_correlation(price1, price2):
    return round(np.corrcoef(price1, price2)[1, 0], 5)


def find_cointegration(price1, price2):
    return round(ts.coint(price1, price2)[1], 5)
