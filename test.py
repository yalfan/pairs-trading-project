import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# calculate z-score
def zscore(series):
    return (series - series.mean()) / np.std(series)


array1 = [42631.64, 42631.64, 42299.24, 41850.79]
series1 = pd.Series(array1)

array2 = [2462.01, 2462.01, 2837.62, 3127.32]
series2 = pd.Series(array2)


series = series1/series2
# series.plot(style='k--')
print(series.rolling(window=2).std())
print(series2.rolling(window=2).mean())

# plt.show()
