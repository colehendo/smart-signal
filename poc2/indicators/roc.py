from pandas import DataFrame
from ta.momentum import roc

# Rate of Change
# gucci
def get_values(candles: DataFrame, indicator_name: str) -> DataFrame:
    results = roc(close=candles["close"], window=12, fillna=True)

    candles[indicator_name] = results
    return candles
