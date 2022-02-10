import pandas
import pandas as pd
import numpy as np
from pymongo import MongoClient
import datetime


def get_values(date1, date2, initial, final):
    d1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
    days = d2 - d1
    days = days.days
    years = days / 365
    cagr_result = round((((final / initial) ** (1/years)) - 1) * 100, 2)
    cagr = str(cagr_result) + "%"

    roi_result = round(((final - initial) / initial) * 100, 2)
    roi = str(roi_result) + "%"
    return {"cagr": cagr, "roi": roi}


# d1 = "2021-10-10"
# d2 = "2021-12-6"
# cagr, roi = get_values(d1, d2, 10000, 20000)

