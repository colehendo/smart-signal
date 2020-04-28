import ta

# Signal Ease of Movement
def run(params, candles, timeframe):
    seom = ta.volume.sma_ease_of_movement(high = candles["h"], low = candles["l"], volume = candles["v"], n = 14, fillna = False)
    print('Signal Ease of Movement')
    print(seom)
    for i in range(0, len(seom)):
        if (i > (len(seom) - 10)):
            print('seom ', i, ': ', round(seom[i], 2))