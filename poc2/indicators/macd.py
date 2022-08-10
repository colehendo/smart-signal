from pandas import DataFrame
from ta.trend import macd_diff

# Moving Average Convergence Divergence
# histogram and signal values match up, but the "macd signal one is not matching up well...
# this one represents the macd fast line on tradingview"
def get_values(candles: DataFrame, indicator_name: str) -> DataFrame:
    results = macd_diff(
        close=candles["close"],
        window_slow=26,
        window_fast=12,
        window_sign=9,
        fillna=False,
    )

    candles[indicator_name] = results
    return candles
