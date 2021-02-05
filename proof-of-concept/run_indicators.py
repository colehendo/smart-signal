import pandas as pd
from scipy.signal import argrelextrema
from importlib import import_module
from itertools import combinations

from shared.data import Info, Pandas

from functools import reduce
from datetime import datetime
from pprint import pprint


def reduce_indicator_results(combined_results: pd.DataFrame, indicators: dict):
    print(f"starting this for {indicators}")
    last_signal = ""
    signals = pd.DataFrame(columns=["unix", "signal"])

    for index, row in combined_results.iterrows():
        indicators[row.indicator] = row.signal

        if row.signal != last_signal:
            if len(set(indicators.values())) == 1:
                last_signal = row.signal
                signals = signals.append(row)

    return signals


class RunIndicators:
    @staticmethod
    def run_single_indicator(
        asset_type: str,
        symbol: str,
        timeframe: str,
        indicator_name: str,
        indicator_params: dict = None,
    ):
        prices = Pandas().csv_to_pandas(
            asset_type=asset_type, symbol=symbol, timeframe=timeframe
        )

        return (
            import_module("indicators." + indicator_name)
            .run(params=indicator_params, candles=prices, timeframe=timeframe)
            .sort_values(by="unix", ignore_index=True)
        )

    def run_indicator_combinations(
        self, asset_type: str, symbol: str, timeframe: str, indicators: {str}
    ):
        indicator_info = Info().get_data(data_name="indicators")

        for indicator in indicator_info:
            if not {indicator, "all"}.intersection(indicators):
                del indicator_info[indicator]
                continue

            # MULTITHREAD THIS!!!!
            indicator_info[indicator]["data"] = self.run_single_indicator(
                asset_type=asset_type,
                symbol=symbol,
                timeframe=timeframe,
                indicator_name=indicator,
                indicator_params=indicator_info[indicator]["params"],
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
                indicator_info[indicator]["data"]
                for indicator in indicator_info
                if indicator in combination
            ]

            if not results_to_combine:
                continue

            combined_results = pd.concat(objs=results_to_combine).sort_values(by="unix")

            if len(combination) == 1:
                results = combined_results

            else:
                results = reduce_indicator_results(
                    combined_results=combined_results,
                    indicators=dict(
                        (indicator, indicator) for indicator in combination
                    ),
                )

            if results.empty:
                continue

            del results["indicator"]

            reduced_combinations.append({"indicators": combination, "results": results})

        for combo in reduced_combinations:
            pprint(combo)

        return reduced_combinations
