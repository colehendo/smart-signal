import json
import pandas as pd
import matplotlib.pyplot as plt
import os


class Info:
    def __init__(self):
        self._dirname = os.path.dirname(__file__)
        self._assets_relpath = "info/assets.json"
        self._timeframes_relpath = "info/timeframes.json"

    def get_asset_data(self):
        filename = os.path.join(self._dirname, self._assets_relpath)
        with open(filename) as a:
            assets = json.load(a)
        return assets

    def get_timeframe_data(self):
        filename = os.path.join(self._dirname, self._timeframes_relpath)
        with open(filename) as tf:
            timeframes = json.load(tf)
        return timeframes


class Pandas:
    def __init__(self):
        self._dirname = os.path.dirname(__file__)
    #     with open("info/assets.json") as assets:
    #         self._assets = json.load(assets)
    #     with open("info/timeframes.json") as timeframes:
    #         self._timeframes = json.load(timeframes)

    def csv_to_pandas(self, asset_type, symbol, timeframe):
        print("flipping csv to pandas")
        csv_relpath = f"candles/{asset_type}/{symbol}_{timeframe}.csv"
        csv_filename = os.path.join(self._dirname, csv_relpath)
        data = pd.read_csv(csv_filename)
        print(data)
        return data


class Visuals:
    def plot(self):
        df = Pandas().csv_to_pandas(asset_type="cryptocurrency", symbol="BTC", timeframe="hour")
        df.plot(x="unix", y="close")
        # df.show()
        # plt.plot(df.loc["unix"], df.loc["close"], data=df)
        # plt.plot([1,2,3], [1,2,3])
        plt.show(block=True)