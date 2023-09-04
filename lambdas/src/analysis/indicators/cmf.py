import ta

# Chaikin Money Flow
# similar to MACD exccept also uses volume.
def run(params, candles, timeframe):
    cmf = ta.volume.chaikin_money_flow(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], n = 20, fillna = False)
    print('Chaikin Money Flow')
    for i in range(0, len(cmf)):
        if (i > (len(cmf) - 10)):
            print('btc close: ', candles["c"][i], ' cmf ', i, ': ', round(cmf[i], 2))