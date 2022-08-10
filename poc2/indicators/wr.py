from pandas import DataFrame
from ta.momentum import williams_r

# Williams %R
def get_values(candles: DataFrame, indicator_name: str) -> DataFrame:
    results = williams_r(
        high=candles["high"],
        low=candles["low"],
        close=candles["close"],
        lbp=14,
        fillna=False,
    )

    candles[indicator_name] = results
    return candles
