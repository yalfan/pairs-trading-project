import pandas as pd
import numpy as np
from pymongo import MongoClient
import datetime
import statsmodels.tsa.stattools as ts


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
    print(ts.coint(price1, price2))
    return ts.coint(price1, price2)


# d1 = "2021-10-10"
# d2 = "2021-12-6"
# cagr, roi = get_values(d1, d2, 10000, 20000)

