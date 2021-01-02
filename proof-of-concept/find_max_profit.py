import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from argparse import ArgumentParser

from pprint import pprint

from shared.data import Info, Pandas


class FindMaxProfit:
    def __init__(self, asset_type: str, symbol: str, timeframe: str, time_gap=0):
        self._asset_type = asset_type
        self._symbol = symbol
        self._timeframe = timeframe

        self._assets = Info().get_asset_data()
        pprint(self._assets)
        self._timeframes = Info().get_timeframe_data()
        pprint(self._timeframes)

        self._time_gap = self.validate_params(time_gap=time_gap)

    def validate_params(self, time_gap,):
        valid_asset_types = list(self._assets.keys())
        if self._asset_type not in valid_asset_types:
            raise ValueError(
                f"{self._asset_type} is not a valid asset type. Options: {valid_asset_types}"
            )

        if self._symbol not in self._assets[self._asset_type]:
            raise ValueError(
                f"The {self._asset_type} {self._symbol} is not available. {self._asset_type} options: {self._assets[self._asset_type]}"
            )

        valid_timeframes = list(self._timeframes.keys())
        if self._timeframe not in valid_timeframes:
            raise ValueError(
                f"{self._timeframe} is not a valid timeframe. Options: {valid_timeframes}"
            )

        if not time_gap:
            time_gap = self._timeframes[self._timeframe].get("time-gap")

        try:
            time_gap = int(time_gap)
        except:
            raise ValueError("time_gap must be an integer.")
        return time_gap

    def max_profit(self):
        print("calling find max profit")
        df = Pandas().csv_to_pandas(
            asset_type=self._asset_type, symbol=self._symbol, timeframe=self._timeframe
        )

        print('dataframe finished calling')

        all_min = df.iloc[
            argrelextrema(df.close.values, np.greater_equal, order=int(self._time_gap / 2))[0]
        ][["unix"]]
        print("mins")
        all_min["sig"] = "sell"
        pprint(all_min)
        all_max = df.iloc[
            argrelextrema(df.close.values, np.less_equal, order=int(self._time_gap / 2))[0]
        ][["unix"]]
        all_max["sig"] = "buy"
        print("maxes")
        pprint(all_max)

        extremes = pd.concat([all_min, all_max])
        extremes.sort_values(by="unix", inplace=True)
        print("extremes")
        pprint(extremes)

        return extremes
