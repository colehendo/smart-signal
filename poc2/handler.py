import os
from argparse import ArgumentParser, Namespace
from concurrent.futures import ThreadPoolExecutor, as_completed
from pandas import DataFrame
from pprint import pprint
from typing import Tuple

from brownian_motion import BrownianMotion
from run_indicators import RunIndicators
from shared.data import Info


def parse_arguments() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "--indicator",
        default="all",
        help="Indicator to run analysis against. Defaults to all.",
    )
    parser.add_argument(
        "--iterations",
        default=1,
        help="Integer value determining number of times to run the full analysis. Defaults to 1.",
        type=int,
    )

    return parser.parse_args()


def get_candle_data(
    dt: float, delta: int, steps: int, lines: int, brownian_motion: BrownianMotion
) -> Tuple[DataFrame, DataFrame]:
    candles, unix = brownian_motion.brownian(
        time_step=dt, delta=delta, steps=steps, total_lines=lines
    )

    results = DataFrame(data=candles, index=unix)
    return results, results


def run_indicator_and_analysis(
    indicator: str,
    candles: DataFrame,
    run_indicators: RunIndicators,
) -> DataFrame:
    indicator_results = run_indicators.get_indicator_values(
        candles=candles, indicator_name=indicator
    )

    return run_indicators.run_indicator_analysis(
        indicator_name=indicator, results=indicator_results
    )


def get_indicaor_data(
    indicators: dict,
    candles: DataFrame,
    # results: DataFrame,
    run_indicators: RunIndicators,
):
    # sell_signals = results
    # buy_signals = results
    max_workers = min(32, os.cpu_count() + 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        indicator_results = {
            executor.submit(
                run_indicator_and_analysis,
                indicator=indicator,
                candles=candles,
                run_indicators=run_indicators,
            )
            for indicator in indicators
        }

        for indicator_result in as_completed(indicator_results):
            analysis_results = indicator_result.result()
            print("here u go chief:")
            from pprint import pprint

            pprint(analysis_results)

            # TODO: Figure out how to determine strength of buy / sell signals
            # for name, result in analysis_results.iteritems():
            # if name.endswith("_sell"):
            #     sell_signals[name.split("_sell")[0]] = result
            # elif name.endswith("_buy"):
            #     buy_signals[name.split("_buy")[0]] = result


def indicator_handler(
    iterations: int,
    dt: float,
    delta: int,
    steps: int,
    lines: int,
    indicators: dict,
    brownian_motion: BrownianMotion,
    run_indicators: RunIndicators,
):
    for i in range(iterations):
        results, candles = get_candle_data(
            dt=dt,
            delta=delta,
            steps=steps,
            lines=lines,
            brownian_motion=brownian_motion,
        )

        get_indicaor_data(
            indicators=indicators,
            candles=candles,
            # results=results,
            run_indicators=run_indicators,
        )

        for j, combo_row in results.iteritems():
            print(j)
            # print(combo_row)


def main():
    args = parse_arguments()
    indicator = args.indicator
    iterations = args.iterations

    # TODO: Figure out how browning works
    delta = 20
    # Total time.
    t = 10.0
    # Number of steps.
    n = 500
    # Time step size
    dt = t / n
    # Number of realizations to generate.
    m = 20

    brownian_motion = BrownianMotion()
    run_indicators = RunIndicators()

    if indicator == "all":
        indicators = Info().get_data(data_name="indicators")
    else:
        indicators = [indicator]

    indicator_handler(
        iterations=iterations,
        dt=dt,
        delta=delta,
        steps=n,
        lines=m,
        indicators=indicators,
        brownian_motion=brownian_motion,
        run_indicators=run_indicators,
    )


if __name__ == "__main__":
    main()
