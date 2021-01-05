import json
import os

import pandas as pd
import matplotlib.pyplot as plt


class Info:
    def __init__(self):
        self._dirname = os.path.dirname(__file__)
        self._assets_relpath = "info/assets.json"
        self._timeframes_relpath = "info/timeframes.json"

    def get_asset_data(self):
        filename = os.path.join(self._dirname, self._assets_relpath)
        with open(filename) as a:
            return json.load(a)

    def get_timeframe_data(self):
        filename = os.path.join(self._dirname, self._timeframes_relpath)
        with open(filename) as tf:
            return json.load(tf)


class Pandas:
    def __init__(self):
        self._dirname = os.path.dirname(__file__)

    def csv_to_pandas(self, asset_type, symbol, timeframe):
        csv_relpath = f"candles/{asset_type}/{symbol}_{timeframe}.csv"
        csv_filename = os.path.join(self._dirname, csv_relpath)

        return pd.read_csv(csv_filename)


class Visuals:
    def plot(self, asset_type, symbol, timeframe, transactions):
        prices = Pandas().csv_to_pandas(
            asset_type=asset_type, symbol=symbol, timeframe=timeframe
        )

        merged_df = pd.merge(left=prices, right=transactions, how="outer", on="unix")
        plt.plot(merged_df.unix, merged_df.close)

        transactions_with_prices = merged_df[merged_df["sig"].notna()]
        for index, row in transactions_with_prices.iterrows():
            plt.annotate(row.sig, (row.unix, row.close))

        plt.show(block=True)
