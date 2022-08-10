import pandas as pd
from argparse import ArgumentParser, Namespace
from logging import getLogger, Formatter, StreamHandler, DEBUG, INFO
from io import StringIO

from brownian_motion import BrownianMotion
from data_handler import DataHandler
from run_indicators import RunIndicators
from shared.data import Info, Visuals
from shared.utils import string_to_bool

from pprint import pprint

logger = getLogger(__name__)


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
        "--transaction_gap",
        "-tg",
        dest="transaction_gap",
        help="INT. Max number of candles to hold a position for the max profit algorithm.",
        type=int,
    )
    parser.add_argument(
        "--second_gap",
        "-sg",
        dest="second_gap",
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


def initialize_logger(output: StringIO):
    logger.setLevel(DEBUG)
    logger.addHandler(hdlr=StreamHandler())

    output_handler = StreamHandler(stream=output)
    output_handler.setLevel(INFO)
    output_handler.setFormatter(Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(hdlr=output_handler)


def get_asset_type(all_assets: [dict], asset_types: [str], symbol: str) -> str:
    key_list = tuple(all_assets.keys())
    for key in key_list:
        if symbol in all_assets[key]:
            return key

    raise ValueError(f"{symbol} does not belong to an asset type")


def set_timeframe_data(timeframe: dict, args: Namespace) -> (int, int, int):
    transaction_gap = args.transaction_gap
    second_gap = args.second_gap

    if not transaction_gap:
        transaction_gap = timeframe["transaction-gap"]
    if not second_gap:
        second_gap = timeframe["second-gap"]

    return transaction_gap, second_gap, timeframe["max-profit-window"]


def main():
    output = StringIO()
    initialize_logger(output=output)

    logger.info("hello!")

    info_class = Info()
    assets = info_class.get_data(data_name="assets")
    timeframes = info_class.get_data(data_name="timeframes")
    asset_types = tuple(assets.keys())

    args = parse_arguments(
        all_assets=assets, asset_types=asset_types, timeframes=timeframes
    )
    symbol = args.symbol
    timeframe = args.timeframe

    transaction_gap, second_gap, max_profit_window = set_timeframe_data(
        timeframe=timeframes[timeframe], args=args
    )

    asset_type = get_asset_type(
        all_assets=assets, asset_types=asset_types, symbol=symbol
    )

    optimal_transactions_with_indicators = DataHandler().compare_max_to_indicators(
        asset_type=asset_type,
        symbol=symbol,
        indicators={"all"},
        timeframe=timeframe,
        transaction_gap=transaction_gap,
        second_gap=second_gap,
        max_profit_window=max_profit_window,
    )

    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None
    ):  # more options can be specified also
        print(optimal_transactions_with_indicators)

    logger.info("goodbye!")

    print(output.getvalue())

    # if args.display_data:
    #     Visuals().plot(
    #         asset_type=asset_type,
    #         symbol=symbol,
    #         timeframe=timeframe,
    #         transactions=transactions,
    #     )


def second_main():
    indicator_info = Info().get_data(data_name="indicators")

    runs = 1
    delta = 20
    # Total time.
    t = 10.0
    # Number of steps.
    n = 500
    # Time step size
    dt = t / n
    # Number of realizations to generate.
    m = 20

    bm = BrownianMotion()
    ri = RunIndicators()

    for i in range(runs):
        out = bm.brownian(time_step=dt, delta=delta, steps=n, total_lines=m)
        # pprint(out)
        print(type(out))

        result = ri.run_single_indicator(
            timeframe="day", indicator_name="rsi", prices=out
        )
        pprint(result)


if __name__ == "__main__":
    second_main()
    # main()
