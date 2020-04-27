import ta

# Bollinger Bands
# Pretty accurate
def run(params, candles, timeframe):
    bb = ta.volatility.BollingerBands(close = candles["c"], n=20, ndev=2)
    mavg = bb.bollinger_mavg()
    print('Bollinger Bands')
    print('bb mavg: ', mavg)
    hband = bb.bollinger_hband()
    print('bb hband: ', hband)
    lband = bb.bollinger_lband()
    print('bb lband: ', lband)
    hband_i = bb.bollinger_hband_indicator() # idk what this is, get rid of these
    print('bb hband_i: ', hband_i)
    lband_i = bb.bollinger_lband_indicator() # idk what this is, get rid of these
    print('bb lband_i: ', lband_i)
    wband = bb.bollinger_wband() # idk what this is, get rid of these
    print('bb wband: ', wband)
    # pband = bb.bollinger_pband()
    # print('bb pband: ', pband)