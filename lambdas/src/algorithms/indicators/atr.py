import ta

# Average True Range
# Pretty solid, maybe off like a few percent for each value
def run(params, candles, timeframe):
    atr = ta.volatility.average_true_range(high = candles["h"], low = candles["l"], close = candles["c"], n = 14, fillna = False)
    print('Average True Range: ', atr)