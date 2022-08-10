from pandas import DataFrame
from ta.momentum import awesome_oscillator

# Awesome Oscillator
# lil off but solid
def get_values(candles: DataFrame, indicator_name: str) -> DataFrame:
    results = awesome_oscillator(
        high=candles["high"], low=candles["low"], window1=5, window2=34, fillna=True
    )

    candles[indicator_name] = results
    return candles
