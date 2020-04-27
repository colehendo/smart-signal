import ta

# Awesome Oscillator
# lil off but solid
def run(params, candles, timeframe):
    ao = ta.momentum.ao(high = candles["h"], low = candles["l"], s = 5, len = 34, fillna = False)
    # print('Awesome Oscillator: ', ao)