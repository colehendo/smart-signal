import numpy as np
import pandas as pd
from scipy.signal import argrelextrema

from shared.data import Pandas


class FindMaxProfit:
    def max_profit(self, asset_type: str, symbol: str, timeframe: str, time_gap: int):
        df = Pandas().csv_to_pandas(
            asset_type=asset_type, symbol=symbol, timeframe=timeframe
        )

        all_min = df.iloc[
            argrelextrema(df.close.values, np.greater_equal, order=int(time_gap / 2))[0]
        ][["unix"]]
        all_min["sig"] = "sell"

        all_max = df.iloc[
            argrelextrema(df.close.values, np.less_equal, order=int(time_gap / 2))[0]
        ][["unix"]]
        all_max["sig"] = "buy"

        extremes = pd.concat([all_min, all_max])
        extremes.sort_values(by="unix", inplace=True)

        return extremes
