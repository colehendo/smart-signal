from pandas import DataFrame
from ta.momentum import stoch

# Stochastic Oscillator
# sr_sig correlates to the %K line on tradingview
def get_values(candles: DataFrame, indicator_name: str) -> DataFrame:
    results = stoch(
        high=candles["high"],
        low=candles["low"],
        close=candles["close"],
        window=14,
        smooth_window=3,
        fillna=True,
    )

    candles[indicator_name] = results
    return candles
