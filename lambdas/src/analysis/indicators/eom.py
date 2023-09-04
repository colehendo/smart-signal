import ta

# Ease of Movement
def run(params, candles, timeframe):
    eom = ta.volume.ease_of_movement(high = candles["h"], low = candles["l"], volume = candles["v"], n = 14, fillna = False)
    print('Ease of Movement')
    for i in range(0, len(eom)):
        if (i > (len(eom) - 10)):
            print('eom ', i, ': ', round(eom[i], 2))