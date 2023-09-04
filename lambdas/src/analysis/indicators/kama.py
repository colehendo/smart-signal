import ta

# Kaufman's Adaptive Moving Average
def run(params, candles, timeframe):
    kama = ta.momentum.kama(close = candles["c"], n = 21, pow1 = 2, pow2 = 30, fillna = False)
    print('Kaufmans Adaptive Moving Average: ', kama)