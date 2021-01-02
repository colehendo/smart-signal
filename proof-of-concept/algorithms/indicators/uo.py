import ta

#Ultimate Oscillator
# gucci
def run(params, candles, timeframe):
    uo = ta.momentum.uo(high = candles["h"], low = candles["l"], close = candles["c"], s = 7, m = 14, len = 28, ws = 4.0, wm = 2.0, wl = 1.0, fillna = False)
    # print('Ultimate Oscillator: ', uo)