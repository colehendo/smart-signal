import ta

# Mass Index, we are using psar to get trend
# good
def run(params, candles, timeframe):
    psar = ta.trend.PSARIndicator(high = candles["h"], low = candles["l"], close = candles["c"], step = 0.02, max_step = 0.2, fillna = False)
    mi = ta.trend.mass_index(high = candles["h"], low = candles["l"], n = 10, n2 = 10, fillna = False)
    print('Mass Index: ', mi)
    signals = []
    trend = "flat"
    last_signal = "hold"

    for i in range(len(mi)):
        curr_mi = mi.iloc[i]
        next_mi = mi.iloc[i+1]
        curr_price = candles["c"][i]
        current_psar = psar.iloc[i]

        #to avoid out of bounds error
        if i+1 == len(mi)-1:
            break

        # when the mass index is over 27 we are very likely to see a reversal in the trend
        # or we are topping out basically
        elif curr_mi > 27 and trend = "up" and last_signal != 'sell':
            if next_mi <= 26.5:
                trend = "down"
                last_signal = "sell"
                signals.append({
                'indicator': 'mi',
                'sig': 'sell',
                'price': float(candles['c'][i]),
                'time': int(candles['t'][i]),
                'tf': timeframe,
                'str': 69
                })
        # when the mass index is over 27 we are very likely to see a reversal in the trend
        # or we are bottoming out
        elif curr_mi > 27 and trend = "down" and last_signal != 'buy':
            if next_mi <= 26.5:
                trend = "up"
                last_signal = "buy"
                signals.append({
                'indicator': 'mi',
                'sig': 'buy',
                'price': float(candles['c'][i]),
                'time': int(candles['t'][i]),
                'tf': timeframe,
                'str': 69
                })
        else: #to get current trend
            if current_psar > curr_price:
                trend = "down"
            elif current_psar < curr_price:
                trend = "up"
            else:
                trend = "flat"


    print("printing mass index signals")
    for i in range(0, len(signals)):
        print(signals[i])

    return signals
