import pandas as pd
from scipy.signal import argrelextrema
from importlib import import_module
from itertools import combinations

from shared.data import Info, Pandas


class RunIndicators:
    def run_single_indicator(
        self,
        asset_type: str,
        symbol: str,
        timeframe: str,
        indicator_name: str,
        indicator_params: dict = None,
    ):
        prices = Pandas().csv_to_pandas(
            asset_type=asset_type, symbol=symbol, timeframe=timeframe
        )

        return import_module("indicators." + indicator_name).run(
            params=indicator_params, candles=prices, timeframe=timeframe
        )

    def reduce_indicator_results(self, combined_results):
        for index, row in combined_results:
            print(row)
            # do shit

    def run_indicator_combinations(
        self, asset_type: str, symbol: str, timeframe: str, indicators: {str}
    ):
        indicator_info = Info().get_data(data_name="indicators")

        for indicator in indicator_info:
            if not {indicator, "all"}.intersection(indicators):
                del indicator_info[indicator]
                continue

            # Make this multithreaded? Test speeds
            indicator_info[indicator]["data"] = self.run_single_indicator(
                asset_type=asset_type,
                symbol=symbol,
                timeframe=timeframe,
                indicator_name=indicator,
                indicator_params=indicator_info["params"],
            )

        indicators = tuple(indicator_info.keys())
        indicator_combinations = [
            combination
            for i in range(len(indicators))
            for combination in tuple(combinations(indicators, i + 1))
        ]

        reduced_combinations = []
        for combination in indicator_combinations:
            results_to_combine = [
                indicator["data"]
                for indicator in indicator_info
                if indicator in combination
            ]

            # Not sure this is the right way to do this...
            combined_results = pd.concat(results_to_combine)

            reduced_combinations.append(
                {
                    "indicators": combination,
                    "results": self.reduce_indicator_results(
                        combined_results=combined_results
                    ),
                }
            )

        return combined_results