import ta

# Simple Moving Average
#shit is broke
def run(params, candles, timeframe):
    sma = ta.trend.sma_indicator(close = candles["c"], n = 12, fillna = False)
    # print('sma: ', sma)