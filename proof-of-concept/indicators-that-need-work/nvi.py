import ta

# Negative Volume Index
def run(params, candles, timeframe):
    nvi = ta.volume.negative_volume_index(close = candles["c"], volume = candles["v"], fillna = False)
    print('Negative Volume Index')
    print(nvi)
    # for i in range(0, len(nvi)):
    #     if (i < 10) or (i > (len(nvi) - 10)):
    #         print('nvi ', i, ': ', nvi[i])