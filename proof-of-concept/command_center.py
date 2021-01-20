from argparse import ArgumentParser
import os

from find_max_profit import FindMaxProfit
from run_indicators import RunIndicators
from shared.data import Info, Visuals
from shared.utils import string_to_bool


def get_argument_choices(
    all_assets: [dict], asset_types: [str], timeframes: [dict]
) -> ([str], [str]):
    timeframe_options = list(timeframes.keys())
    symbol_options = [
        symbol for asset_name in asset_types for symbol in all_assets[asset_name]
    ]

    return sorted(symbol_options), sorted(timeframe_options)


def parse_arguments(all_assets: [dict], asset_types: [str], timeframes: [dict]):
    symbol_options, timeframe_options = get_argument_choices(
        all_assets=all_assets, asset_types=asset_types, timeframes=timeframes
    )

    parser = ArgumentParser()
    parser.add_argument(
        "--symbol",
        "-s",
        choices=symbol_options,
        dest="symbol",
        help="Symbol of the asset to run the algorithm on. AAPL, BTC, USD, etc.",
        required=True,
    )
    parser.add_argument(
        "--timeframe",
        "-tf",
        choices=timeframe_options,
        dest="timeframe",
        help="Period of time per candle.",
        required=True,
    )
    parser.add_argument(
        "--time_gap",
        "-tg",
        dest="time_gap",
        help="INT. Max number of candles to hold a position for the max profit algorithm.",
        type=int,
    )
    parser.add_argument(
        "--display_data",
        "-dd",
        default=True,
        dest="display_data",
        help="BOOL. Whether to display the data in a line graph or not. Default is True.",
        type=string_to_bool,
    )
    return parser.parse_args()


def get_asset_type(all_assets: [dict], asset_types: [str], symbol: str) -> str:
    key_list = tuple(all_assets.keys())
    for key in key_list:
        if symbol in all_assets[key]:
            return key

    raise ValueError(f"{symbol} does not belong to an asset type")


def main():
    info_class = Info()
    assets = info_class.get_data(data_name="assets")
    timeframes = info_class.get_data(data_name="timeframes")
    asset_types = tuple(assets.keys())

    args = parse_arguments(
        all_assets=assets, asset_types=asset_types, timeframes=timeframes
    )
    symbol = args.symbol
    timeframe = args.timeframe
    time_gap = args.time_gap
    if not time_gap:
        time_gap = int(timeframes[timeframe].get("time-gap"))

    asset_type = get_asset_type(
        all_assets=assets, asset_types=asset_types, symbol=symbol
    )

    transactions = RunIndicators().run_single_indicator(
        asset_type=asset_type, symbol=symbol, timeframe=timeframe, indicator_name="roc"
    )

    # transactions = FindMaxProfit().max_profit(
    #     asset_type=asset_type, symbol=symbol, timeframe=timeframe, time_gap=time_gap
    # )

    if args.display_data:
        Visuals().plot(
            asset_type=asset_type,
            symbol=symbol,
            timeframe=timeframe,
            transactions=transactions,
        )


if __name__ == "__main__":
    main()
