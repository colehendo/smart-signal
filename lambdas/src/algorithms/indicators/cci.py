import ta

# Commodity Channel Index
def run(params, candles, timeframe):
    cci = ta.trend.cci(high = candles["h"], low = candles["l"], close = candles["c"], n = 20, c = 0.015, fillna = False)
    print('Commodity Channel Index: ', cci)