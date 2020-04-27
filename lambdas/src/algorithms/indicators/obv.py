import ta

# On-Balance Volume
#Pretty pooop
def run(params, candle, timeframe):
    obv = ta.volume.on_balance_volume(close = candles["c"], volume = candles["v"], fillna = False)
    print('On-Balance Volume')
    for i in range(0, len(obv)):
        if (i > (len(obv) - 10)):
            print('btc close: ', candles["c"][i], ' obv ', i, ': ', round(obv[i], 2))