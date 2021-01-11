import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

from shared.data import Pandas


class FindMaxProfit:
    def max_profit(self, asset_type: str, symbol: str, timeframe: str, time_gap: int):
        prices = Pandas().csv_to_pandas(
            asset_type=asset_type, symbol=symbol, timeframe=timeframe
        )

        all_min = prices.iloc[
            argrelextrema(prices.close.values, np.greater_equal, order=int(time_gap / 2))[0]
        ][["unix"]]
        all_min["signal"] = "sell"

        all_max = prices.iloc[
            argrelextrema(prices.close.values, np.less_equal, order=int(time_gap / 2))[0]
        ][["unix"]]
        all_max["signal"] = "buy"

        extremes = pd.concat([all_min, all_max])
        extremes.sort_values(by="unix", inplace=True)

        return extremes
