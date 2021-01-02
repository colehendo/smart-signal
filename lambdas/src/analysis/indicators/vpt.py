import ta

# Volume-price Trend
def run(params, candles, timeframe):
    obv = ta.volume.on_balance_volume(close = candles["c"], volume = candles["v"], fillna = False)
    print('Volume-price Trend: ', vpt)
    # for i in range(0, len(vpt)):
    #     print(vpt[i])