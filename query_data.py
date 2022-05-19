from upload_data import *

# d1 = "2021-10-10"
# d2 = "2021-12-6"
client = MongoClient("mongodb+srv://yalfan22:yale2004@cluster0.qszrw.mongodb.net/test", connect=False)
db = client.pairs_trading

collections = []
for i in db.list_collection_names():
    collections.append(db[i])

coins = {db.list_collection_names()[i]: collections[i] for i in range(len(db.list_collection_names()))}

# print(coins)


def find_best_pairs(date1, date2):
    from values import find_correlation, find_cointegration
    coin_symbols = ["btc", "eth", "ltc", "xrp", "bch"]
    values_to_return = []
    for i in range(len(coin_symbols)-1):
        for j in range(i+1, len(coin_symbols)):
            prices1 = np.array(get_data(date1, date2, coin_symbols[i])[0])
            prices2 = np.array(get_data(date1, date2, coin_symbols[j])[0])
            print("prices 1 %s %s" % (len(prices1), coin_symbols[i]))
            print("prices 2 %s %s" % (len(prices2), coin_symbols[j]))
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


def auto_update_csv(coin_str):
    coin = coins[coin_str]
    yesterday = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    last_date = coin.find().limit(1).sort([('$natural', -1)])[0]['Date'].date()
    first_date = coin.find()[0]['Date'].date()
    print(last_date)
    print(first_date)
    print(coin_str)
    if last_date.strftime('%Y-%m-%d') != yesterday and first_date.strftime("%Y-%m-%d") != yesterday:
        if coin_str in ['btc', 'eth', 'bch', 'xrp', 'ltc']:
            print("updated %s date!" % coin_str)
            coin_symbol = coin_str.upper() + "-USD"
            update_csv_db(coin_symbol, last_date)


def check_dates(coin_str1, coin_str2, start_date, end_date):
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    auto_update_csv(coin_str1)
    auto_update_csv(coin_str2)
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
