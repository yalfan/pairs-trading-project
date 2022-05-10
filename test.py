import datetime
date1 = datetime.datetime.strptime("2022-06-06", "%Y-%m-%d")
print(date1, type(date1))
date2 = datetime.datetime.strptime("2020-06-06", "%Y-%m-%d")
print(date2, type(date2))
print(date1.strftime("%Y-%m-%d") > date2.strftime("%Y-%m-%d"))
