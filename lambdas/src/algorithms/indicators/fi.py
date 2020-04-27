import ta

# Force Index
# Multiplies the change in volume * price for each day
# probably drop this hoe bc too inconsistent
def run(params, candles, timeframe):
    fi = ta.volume.force_index(close = candles["c"], volume = candles["v"], n = 13, fillna = False)
    print('Force Index')
    for i in range(0, len(fi)):
        if (i > (len(fi) - 10)):
            print('fi ', i, ': ', round(fi[i], 2))