import json
import os

import pandas as pd
import matplotlib.pyplot as plt


class Info:
    def get_data(self, data_name: str):
        dirname = os.path.dirname(__file__)
        file_relpath = f"info/{data_name}.json"
        filename = os.path.join(dirname, file_relpath)
        with open(filename) as f:
            return json.load(f)


class Pandas:
    def csv_to_pandas(self, asset_type, symbol, timeframe):
        dirname = os.path.dirname(__file__)
        csv_relpath = f"candles/{asset_type}/{symbol}_{timeframe}.csv"
        csv_filename = os.path.join(dirname, csv_relpath)

        return pd.read_csv(csv_filename)


class Visuals:
    def plot(self, asset_type, symbol, timeframe, transactions):
        prices = Pandas().csv_to_pandas(
            asset_type=asset_type, symbol=symbol, timeframe=timeframe
        )

        merged_df = pd.merge(left=prices, right=transactions, how="outer", on="unix")
        plt.plot(merged_df.unix, merged_df.close)

        transactions_with_prices = merged_df[merged_df["signal"].notna()]
        for index, row in transactions_with_prices.iterrows():
            plt.annotate(row.signal, (row.unix, row.close))

        plt.show(block=True)
