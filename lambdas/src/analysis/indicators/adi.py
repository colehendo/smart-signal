import ta

# # Accumulation/Distribution Index
# # Works best in a ranging period(so maybe after huge moves up or down),
# # does not work well when market is trending hard, good for locating trend reversals through top/bottom divergences
# # The AD line compares the strength of the open to the strength of the close divided by the range
def run(params, candles, timeframe):
    adi = ta.volume.acc_dist_index(high = candles["h"], low = candles["l"], close = candles["c"], volume = candles["v"], fillna = False)
    print("Accumulation/Distribution Index")
    for i in range(0, len(adi)):
        if (i > (len(adi) - 10)):
            print('btc close: ', candles["c"][i], ' adi ', i, ': ', round(adi[i], 2))