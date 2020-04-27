import ta

# Williams %R
#gucci
def run(params, candles, timeframe):
    wr = ta.momentum.wr(high = candles["h"], low = candles["l"], close = candles["c"], lbp = 14, fillna = False)
    # print('Williams %R: ', wr)