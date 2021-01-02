import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from argparse import ArgumentParser

from pprint import pprint

from shared.data import Info, Pandas


def add_arguments():
    parser = ArgumentParser()
    parser.add_argument(
        "--asset_type",
        type=str,
        dest="asset_type",
        help="The type of asset to find the max for.",
        required=True,
    )
    parser.add_argument(
        "--symbol",
        type=str,
        dest="symbol",
        help="The symbol of the asset to find the max for.",
        required=True,
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        dest="timeframe",
        help="The length of each candle. minute, hour, or day.",
        required=True,
    )
    parser.add_argument(
        "--time_gap",
        type=str,
        dest="time_gap",
        help="The max number of candles to hold an asset before forcing a trade.",
    )
    return parser.parse_args()


def validate_params(
    assets: dict,
    timeframes: dict,
    asset_type: str,
    symbol: str,
    timeframe: str,
    time_gap,
):
    valid_asset_types = list(assets.keys())
    if asset_type not in valid_asset_types:
        raise ValueError(
            f"{asset_type} is not a valid asset type. Options: {valid_asset_types}"
        )

    if symbol not in assets[asset_type]:
        raise ValueError(
            f"The {asset_type} {symbol} is not available. {asset_type} options: {assets[asset_type]}"
        )

    valid_timeframes = list(timeframes.keys())
    if timeframe not in valid_timeframes:
        raise ValueError(
            f"{timeframe} is not a valid timeframe. Options: {valid_timeframes}"
        )

    if not time_gap:
        time_gap = timeframes[timeframe].get("time_gap")

    try:
        time_gap = int(time_gap)
    except:
        raise ValueError("time_gap must be an integer.")
    return time_gap


def find_max_profit(timeframes: dict, asset_type: str, symbol: str, timeframe: str):
    df = Pandas().csv_to_pandas(
        asset_type=asset_type, symbol=symbol, timeframe=timeframe
    )

    print('dataframe finished calling')

    all_min = df.iloc[
        argrelextrema(df.close.values, np.greater_equal, order=int(time_gap / 2))[0]
    ][["unix"]]
    print("mins")
    all_min["sig"] = "sell"
    pprint(all_min)
    all_max = df.iloc[
        argrelextrema(df.close.values, np.less_equal, order=int(time_gap / 2))[0]
    ][["unix"]]
    all_max["sig"] = "buy"
    print("maxes")
    pprint(all_max)

    extremes = pd.concat([all_min, all_max])
    extremes.sort_values(by="unix", inplace=True)
    print("extremes")
    pprint(extremes)

    return extremes


def main():
    print("starting out")
    args = add_arguments()
    asset_type = args.asset_type
    symbol = args.symbol
    timeframe = args.timeframe
    time_gap = args.time_gap

    assets = Info().get_asset_data()
    pprint(assets)
    timeframes = Info().get_timeframe_data()
    pprint(timeframes)

    pprint("okay here we go fam")

    time_gap = validate_params(
        assets=assets,
        timeframes=timeframes,
        asset_type=asset_type,
        symbol=symbol,
        timeframe=timeframe,
        time_gap=time_gap,
    )

    print("calling find max profit")

    return find_max_profit(
        asset_type=asset_type, symbol=symbol, timeframe=timeframe, time_gap=time_gap
    )


if __name__ == "__main__":
    main()
