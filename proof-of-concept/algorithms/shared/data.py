import json
import pandas as pd
import matplotlib.pyplot as plt


class Info:
    def get_asset_data(self):
        with open("../info/assets.json") as assets:
            _assets = json.load(assets)
        return _assets

    def get_timeframe_data(self):
        with open("../info/timeframes.json") as timeframes:
            _timeframes = json.load(timeframes)
        return _timeframes


class Pandas:
    # def __init__(self):
    #     with open("info/assets.json") as assets:
    #         self._assets = json.load(assets)
    #     with open("info/timeframes.json") as timeframes:
    #         self._timeframes = json.load(timeframes)

    def csv_to_pandas(self, asset_type, symbol, timeframe):
        print("flipping csv to pandas")
        data = pd.read_csv(f"../candles/{asset_type}/{symbol}_{timeframe}.csv")
        print(data)
        return data


# class Visuals:
    # def __init__(self)