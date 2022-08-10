from pandas import DataFrame, Series
from ta.momentum import rsi
from typing import List, Dict
from inspect import currentframe


# Relative Strength Index
def get_values(candles: DataFrame, indicator_name: str) -> DataFrame:
    results = rsi(close=candles["close"], window=14, fillna=False)

    candles[indicator_name] = results
    return candles


def analysis_handler(
    signal_class, analysis_results: DataFrame, indicator_name: str, signal: str
):  # -> List[Dict[str, Series]]:
    method_functions = [
        function for function in dir(signal_class) if not function.startswith("_")
    ]

    for function in method_functions:
        result = getattr(signal_class, function)(signal=signal)
        analysis_results[f"{indicator_name}_{function}_{signal}"] = result
    # return [
    #     {f"{indicator_name}_{function}_{signal}": getattr(method, function)()}
    #     for function in method_functions
    # ]


def analyze(data: DataFrame, indicator_name: str) -> DataFrame:
    analysis_results = DataFrame(index=data["unix"])
    signal_classes = [
        {"signal": "sell", "class": Sell(data=data, indicator_name=indicator_name)},
        {"signal": "buy", "class": Buy(data=data, indicator_name=indicator_name)},
    ]

    for signal_class in signal_classes:
        analysis_handler(
            signal_class=signal_class["class"],
            analysis_results=analysis_results,
            indicator_name=indicator_name,
            signal=signal_class["signal"],
        )

    return analysis_results


class Sell:
    def __init__(self, data: DataFrame, indicator_name: str):
        self.data = data
        self.indicator_name = indicator_name

    def over_70(self, signal: str) -> Series:
        function_name = currentframe().f_code.co_name
        signals = Series(name=function_name, index=self.data["unix"])

        sell = 70
        top = top_rsi = None

        for index, row in self.data.iterrows():
            curr_rsi = row[self.indicator_name]
            curr_price = row["close"]

            if not top or top < curr_price:
                top = curr_price
                top_rsi = curr_rsi

            if (curr_rsi > 100) or (curr_rsi < 0):
                continue

            if curr_rsi > sell and (curr_price < top and curr_rsi > top_rsi):
                signals.at[]
                signal_timestamps.append(index)

        return Series(data=signal_timestamps, name=function_name)


class Buy:
    def __init__(self, data: DataFrame, indicator_name: str):
        self.data = data
        self.indicator_name = indicator_name

    def under_30(self, signal: str) -> Series:
        signal_timestamps = []
        function_name = currentframe().f_code.co_name

        buy = 30
        bottom = bottom_rsi = None

        for index, row in self.data.iterrows():
            curr_rsi = row["rsi"]
            curr_price = row["close"]

            if not bottom or bottom > curr_price:
                bottom = curr_price
                bottom_rsi = curr_rsi

            if (curr_rsi > 100) or (curr_rsi < 0):
                continue

            if curr_rsi < buy and (curr_price < bottom and curr_rsi > bottom_rsi):
                signal_timestamps.append(index)

        return Series(data=signal_timestamps, name=function_name)


if __name__:
    analyze(DataFrame(), "blah")
