import numpy as np

from find_max_profit import FindMaxProfit
from run_indicators import RunIndicators


class DataHandler:
    def compare_max_to_indicators(
        self,
        asset_type: str,
        symbol: str,
        indicators: set,
        timeframe: str,
        transaction_gap: int,
        second_gap: int,
        max_profit_window: int,
    ):
        max_profit = FindMaxProfit().max_profit(
            asset_type=asset_type,
            symbol=symbol,
            timeframe=timeframe,
            transaction_gap=transaction_gap,
        )

        max_profit["indicator_combinations"] = np.empty((len(max_profit), 0)).tolist()

        indicator_results = RunIndicators().run_indicator_combinations(
            asset_type=asset_type,
            symbol=symbol,
            timeframe=timeframe,
            indicators=indicators,
        )

        for combination in indicator_results:
            for i, combo_row in combination["results"].iterrows():
                for index, max_row in max_profit.iterrows():
                    if max_row.signal != combo_row.signal:
                        continue

                    if (
                        abs(max_row.unix - combo_row.unix)
                        <= second_gap * max_profit_window
                    ):
                        max_row["indicator_combinations"].append(
                            combination["indicators"]
                        )

                    if max_row.unix > combo_row.unix:
                        break

        return max_profit
